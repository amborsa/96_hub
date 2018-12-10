// nRF24L01 radio transceiver external libraries
#include <SPI.h>
#include <RF24.h>
#include <nRF24L01.h>
#include <printf.h>
#include <Wire.h>
#include <EEPROM.h>
#include <Protocentral_MAX30205.h>

// set whether 5.0 or 3.3 volt device
float Vcc = 3.3;

// chip select and RF24 radio setup pins
#define CE_PIN 9
#define CSN_PIN 10
RF24 radio(CE_PIN,CSN_PIN);

//// Communication variables and initialization ////

// setup radio pipe addresses for each slave node
char nodeAddress = 0x04;
byte newNodeID;

// array type to collect from master {age, alarm state}
typedef union writeArrayT {
	struct {
		unsigned long age;
		bool alarmstate;
	} asStruct;
	byte asbytes[5];
} writeArrayT;

// global write array
writeArrayT writeArray;

//// Heart and Respiratory and FRAM variables and initialization ////

// Adafruit_FRAM_I2C fram     = Adafruit_FRAM_I2C();
MAX30205 tempSensor;

typedef union timevalue{
	unsigned long aslong;
	byte asbytes[4];
} timevalue;

typedef union voltvalue{
	int asint;
	byte asbytes[2];
} voltvalue;

typedef struct datatuplevalues{
	timevalue timev;
	voltvalue voltv;
} datatuplevalues;

typedef union datatuple{
	datatuplevalues asvalues;
	byte asbytes[6];
} datatuple;

typedef union sensorarray{
	struct {
		unsigned long stime;
		float HR;
		float RR;
		float temp;
	} asvalues;
	byte asbytes[16];
} sensorarray;
sensorarray sensdata;

timevalue timevalue1;
timevalue timevalue2;

datatuple rambuffer[30];
byte ramn = 0;
int ignore = 0;
float ECGaverage = 0.0;
unsigned long ECGtotal = 0;
float previousECGaverage = 0.0;
int Rwaves[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};


int promAddr = 0;
int maxpromAddr = 0;

byte iteration_delay = 5;
byte ms_delay = 5;

unsigned long times[2];

#define downLED 3
#define upLED 4



////  main loop variables ////

// byte tuplesk = 0;
unsigned long loop_start_time;


//// alarm state variables ////

#define warningLED 5

// threshold values for alarm states

// note: as of now, these values sort of ignore children <1yr of age
float uppertemp = 37.0;
float lowertemp = 34.0;

bool hubalarm = false;
byte eff_age = 15;

typedef struct alarmvals{
	int upperHR;
	int lowerHR;
	int upperRR;
	int lowerRR;
} alarmvals;



/* Function: setup
 *    Initialises the system wide configuration and settings prior to start
 */
 
void setup() {

	//// communication setup ////

	// setup serial communications for basic program display
	Serial.begin(9600);
	Serial.println("[*][*][*] Beginning nRF24L01+ ack-payload slave device program [*][*][*]");

	// ----------------------------- RADIO SETUP CONFIGURATION AND SETTINGS -------------------------// 
	
	radio.begin();
	
	// set power level of the radio
	radio.setPALevel(RF24_PA_LOW);
	// set RF datarate
	radio.setDataRate(RF24_250KBPS);
	// set radio channel to use - ensure it matches the target host
	radio.setChannel(0x76);
	// open a reading pipe on the chosen address for selected node
	radio.openReadingPipe(1, nodeAddress);
	// enable ack payload - slave reply with data using this feature
	radio.enableAckPayload();
	// preload the payload with initial data - sent after an incoming message is read
	radio.writeAckPayload(1, &sensdata, sizeof(sensdata));
	// print radio config details to console
	printf_begin();
	radio.printDetails();
	// start listening on radio
	radio.startListening();
	
	// --------------------------------------------------------------------------------------------//


	//// Sensing and FRAM setup ////

	pinMode(A0, INPUT);
	pinMode(A6, INPUT);
	pinMode(7, OUTPUT);

	Wire.begin(MAX30205_ADDRESS);
	tempSensor.begin();

	//// alarm setup ////
	pinMode(upLED, OUTPUT);
	pinMode(downLED, OUTPUT);
	pinMode(warningLED, OUTPUT);


  sensdata.asvalues.stime = 1;
  sensdata.asvalues.temp = 38.0;
  sensdata.asvalues.HR = 60.0;
  sensdata.asvalues.RR = 18;

}

void loop() {

	loop_start_time = millis(); // start time of the loop for determining data collection time

	// gets HR RR and Temp
	getSensorData(sensdata.asbytes);
	// writebytes(startSendAddr + tuplesk * sizeof(sensdata.asbytes), sensdata.asbytes, sizeof(sensdata.asbytes));
	// tuplesk = tuplesk + 1;

	// Serial.print("tuplesk:");
	// Serial.println(tuplesk);

//  sensdata.asvalues.stime = sensdata.asvalues.stime;
//  sensdata.asvalues.HR = sensdata.asvalues.HR + 0.1;
//  sensdata.asvalues.RR = sensdata.asvalues.RR + 0.1;
//  sensdata.asvalues.temp = sensdata.asvalues.temp;

  Serial.println("about to send data!");
  bool works = false;
	while((millis()-loop_start_time)<30000 && works == false){
		// Serial.println("in while loop");
		// transmit current preloaded data to master device if message request received
		// readbytes(startSendAddr + (tuplesk - 1) * sizeof(sensdata.asbytes), sensdata.asbytes, sizeof(sensdata.asbytes));
		// sensdata.asvalues.stime = (millis() - sensdata.asvalues.stime) / 1000 / 60;
		// sensdata.asvalues.stime = 4000;
		// sensdata.asvalues.temp = 40.0;
		// sensdata.asvalues.HR = 60.0;
		// sensdata.asvalues.RR = 21.0;
		// Serial.print("tuplesk");
		// Serial.print(tuplesk);

		// bool success = radioCheckAndReply(sensdata.asbytes, sizeof(sensdata.asbytes));
		// Serial.print("success:");
		// Serial.println(success);
//    if (success == true) {
//      tuplesk = tuplesk - 1;
//      Serial.println("tuplesk going down");
//    }

		works = radioCheckAndReply(sensdata.asbytes,sizeof(sensdata.asbytes));
		if (works==true) {
			Serial.println("We had a connection!");
			// sensorData.asvalues.stime++;
			// sensorData.asvalues.HR = sensorData.asvalues.HR + 0.1;
			// sensorData.asvalues.RR = sensorData.asvalues.RR + 0.1;

       Serial.print("\tstime:");
       Serial.print(sensdata.asvalues.stime);
       Serial.print("\ttemp:");
       Serial.println(sensdata.asvalues.temp);
       Serial.print("\tHR:");
       Serial.println(sensdata.asvalues.HR);
       Serial.print("\tRR:");
       Serial.println(sensdata.asvalues.RR);
     
		}
	}

  Serial.println("pausing for 10 seconds");
//	while((millis()-loop_start_time)<(10000)){
//		Serial.println("pasuing...");
//		delay(1000);
//	}

  delay(60000);
		
	
}

/* Function: radioCheckAndReply
 *    sends the preloaded node data over the nrf24l01+ radio when
 *    a message is received by the master
 */
// Runs after the sensor code for a max total time of 10 mins
bool radioCheckAndReply(byte* sendbytes, short sendsize) {
	writeArray.asStruct.age = 129;
	// Check to see if node is ready to be set
	if (nodeAddress==0x00) {
		bool newnode = checkNodeSet();
		if (newnode) {
			return true;
		}
		else{
			return false;
		}
	}
	else {
		if (radio.available()){
			Serial.println("Trying to get master connection.");
			radio.read(writeArray.asbytes,sizeof(writeArray.asbytes));
			// Check for overwrite procedure first
			if (writeArray.asStruct.age == 0 && writeArray.asStruct.alarmstate == true) {
				nodeAddress = 0x00;
				radio.openReadingPipe(1,nodeAddress);
				radio.openWritingPipe(nodeAddress);
				if (radio.available()) {
					char success = 0xf1;
					radio.writeAckPayload(1,&success,sizeof(success));
					Serial.print("THIS IS THE THING BEING PASSED INTO THE REWRITTEN PIPE ");
					Serial.println(success);
					Serial.println("Our device node address has been successfully overwritten back to the zero pipe");
				}
			}
			// If overwrite procedure not activated
			else {
				Serial.print("The patient's age is: ");
				Serial.print(writeArray.asStruct.age);
				Serial.print(". Our alarm state is: ");
				if (writeArray.asStruct.alarmstate==false) {
					Serial.println("no alarm. ");
				}
				else {
					Serial.println("ALARM! ");
				}
				radio.writeAckPayload(1,sendbytes,sendsize);
				hubalarm = writeArray.asStruct.alarmstate;
				if(writeArray.asStruct.age > 180){
					eff_age = 15;
				}
				else {
					eff_age = int(writeArray.asStruct.age / 12.0);
				}
				
				return(true);
			}
		}
		else {
			return(false);
		}
	}
}
bool checkNodeSet(void) {
	// First check for new device protocol
	// marker to indicate successful rewrite of slave from 0 pipe
	Serial.println("Trying to get node assignment.");
	char rewrite = 0xff;
	// Check if the master has a 00 pipe open
	if (radio.available()) {
		// Pull the master's data (should be new node number)
		radio.read(&newNodeID, sizeof(newNodeID));
		// save to be stored by child
		nodeAddress = newNodeID;
		// Print new node
		Serial.print("The new node address of this device is: ");
		Serial.println(nodeAddress,DEC);
	}
	// Open the new node permanently as the reading pipe
	radio.openReadingPipe(1,nodeAddress);
	radio.openWritingPipe(nodeAddress);
	int rewritetime = millis();
	radio.writeAckPayload(1,&rewrite,sizeof(rewrite));
	if (nodeAddress != 0x00) {
		return true;
	}
	else {
		return false;
	}
}


void getSensorData(byte* bytes){
	
	Serial.println("--");
	Serial.println("--");
	Serial.println("--");
	Serial.println("gathering new ECG data for 15 seconds");
	promAddr = 0;
	
	digitalWrite(7, HIGH);
	
	maxpromAddr = gatherECGpeaks(15, times);
	maxpromAddr = maxpromAddr - 6;
	digitalWrite(7, LOW);

	Serial.println("--");
	Serial.println("--");
	Serial.println("--");
	Serial.println("maxpromAddr:");
	Serial.print(maxpromAddr);
	Serial.println("done!");

	datatuple starttuple;
	readEEPROM(0, starttuple.asbytes, 6);

	datatuple stoptuple;
	readEEPROM(maxpromAddr, stoptuple.asbytes, 6);

	//long HRdeltatime = stoptuple.asvalues.timev.aslong - starttuple.asvalues.timev.aslong;
	Serial.println(times[1]);
	Serial.println(times[0]);
	long HRdeltatime = times[1] - times[0];

	int peaks = maxpromAddr / 6;

	float HR = peaks/(HRdeltatime / 1000.0) * 60.0;

	float RR = calculateRR(maxpromAddr, HRdeltatime);

	float temp = 0.0;

	unsigned long starttemptime = millis();
	int k = 0;

	while(millis() - starttemptime < 1500){
		temp = temp + tempSensor.getTemperature();
		k = k + 1;
		delay(100);
	}
	temp = temp / k;

	// temp = tempSensor.getTemperature();

	Serial.println("Results:\tpeaks\t");
	Serial.print(peaks);
	Serial.print("\tHRdeltatime\t");
	Serial.print(HRdeltatime);
	Serial.print("\tHeart Rate:\t");
	Serial.print(HR);
	Serial.print("\tResp Rate:\t");
	Serial.print(RR);
	Serial.print("");
	Serial.print("temp:");
	Serial.println(temp);
	
	sensdata.asvalues.HR = HR;
	sensdata.asvalues.RR = RR;
	sensdata.asvalues.temp = temp;
	
	bytes = sensdata.asbytes;

	checkAlarm2(sensdata);

	return bytes;
	
}

float calculateRR(int maxpromAddr, float deltatime) {

	short t = 0;
	
	for(int n = 6; n < maxpromAddr; n = n + 6) {

		datatuple datatuple1;
		datatuple datatuple2;
		datatuple datatuple3;
		readEEPROM(n-6, datatuple1.asbytes, 6);
		readEEPROM(n, datatuple2.asbytes, 6);
		readEEPROM(n+6, datatuple3.asbytes, 6);

		if((datatuple2.asvalues.voltv.asint > datatuple1.asvalues.voltv.asint) && (datatuple2.asvalues.voltv.asint > datatuple3.asvalues.voltv.asint)) {
			unsigned long peaktime = datatuple2.asvalues.timev.aslong;
			t = t + 1;
		}
	}

	float RespRate = t/(deltatime / 1000.0) * 60.0;
	return RespRate;
}



int gatherECGpeaks(unsigned long duration, unsigned long* times) {
	
	int iteration = 0;
	int rawread = 0;

	Serial.println("5 seconds to calibrate without messing up data...");
	while(iteration < 1000) {
		iteration = iteration + 1;
		rawread = analogRead(A0);

		if(rawread > 950) {
			digitalWrite(downLED, HIGH);
		}
		else if(rawread < 50) {
			digitalWrite(upLED, HIGH);
		}
		else {
			digitalWrite(downLED, LOW);
			digitalWrite(upLED, LOW);
		}

		delay(ms_delay);
	}

	iteration = 0;
	
	// get initial ECG average before looking for peaks
	ECGtotal = 0;
	float ECGmax = 0.0;

	Serial.println("getting averages and baseline threshold...");
	while (iteration < 1000) {
		
		// check status of raw input
		rawread = analogRead(A0);
		// Serial.print("rawread:");
		// Serial.println(rawread);
		if(rawread > 600) {
			digitalWrite(downLED, HIGH);
		}
		else if(rawread < 50) {
			digitalWrite(upLED, HIGH);
		}
		else {
			digitalWrite(downLED, LOW);
			digitalWrite(upLED, LOW);
		}

		// read filtered output
		iteration = iteration + 1;
		int value = analogRead(A1);
		ECGtotal = ECGtotal + value;
		if(value > ECGmax) {
			ECGmax = value;
		}
		delay(ms_delay);
	}

	
	float ECGaverage = ECGtotal/1000.0;
	Rwaves[0] = ECGmax - ECGaverage;
	Rwaves[1] = ECGmax - ECGaverage;
	Rwaves[2] = ECGmax - ECGaverage;
	Rwaves[3] = ECGmax - ECGaverage;
	Rwaves[4] = ECGmax - ECGaverage;
	Rwaves[5] = ECGmax - ECGaverage;
	Rwaves[6] = ECGmax - ECGaverage;
	Rwaves[7] = ECGmax - ECGaverage;
	Rwaves[8] = ECGmax - ECGaverage;
	Rwaves[9] = ECGmax - ECGaverage;

	Serial.print("calibration:");
	Serial.print("\tECGmax:\t");
	Serial.print(ECGmax);
	Serial.print("\tECG average:\t");
	Serial.print(ECGaverage);
	Serial.print("\tRwaves\t");
	Serial.print(Rwaves[3]);
	Serial.println("");

	iteration = 0;
	unsigned long starttime = millis();
	times[0] = starttime;

	Serial.print("gathering data now for ");
	Serial.print(duration);
	Serial.print(" seconds");
	// if not over polling duration, continue to take live data
	while((millis() - starttime) < duration * 1000) {

		// initialize datatuple
		datatuple vtuple;

		// iterate ignore downward
		ignore = ignore - 1;
		iteration = iteration + 1;

		// read and timestamp data
		vtuple.asvalues.timev.aslong = millis();
		vtuple.asvalues.voltv.asint = analogRead(A1);

		// check status of raw input
		int rawread = analogRead(A0);
		// Serial.print("rawread:");
		// Serial.println(rawread);
		if(rawread > 600) {
			digitalWrite(downLED, HIGH);
		}
		else if(rawread < 50) {
			digitalWrite(upLED, HIGH);
		}
		else {
			digitalWrite(downLED, LOW);
			digitalWrite(upLED, LOW);
		}

		// keep track of ram iterator
		if(ramn >= 29) {
			ramn = 0;
		}
		else {
			ramn = ramn + 1;
		}

		rambuffer[ramn].asvalues = vtuple.asvalues;

		// calculate running ECG voltage average
		if (iteration > 30) {
			ECGtotal = 0;
			for(int i = 0; i < 30; i++) {
				ECGtotal = ECGtotal + rambuffer[i].asvalues.voltv.asint;
			}
			ECGaverage = ECGtotal/30.0;
		}

		// calculate threshold for detecting R wave
		float threshold;
		for(int i = 0; i < 10; i++) {
			threshold = Rwaves[i] + threshold;
		}
		threshold = (threshold/10.0) * (Vcc/1024) * 0.6;

		// when we first pass threshold, set ignoring
		if((((rambuffer[ramn].asvalues.voltv.asint - ECGaverage)* Vcc/1024) > threshold) && (ignore < 0)) {
			// peak upcoming!!
			Serial.println("------");
			Serial.println("setting ignore, past threshold"); 
			ignore = 50;
			previousECGaverage = ECGaverage;
		}

//    Serial.print("\tignore:");
//    Serial.println(ignore);

		// once we've gone through enough of the iterations, find the max (the R wave)
		if(ignore == 0) {

			ECGmax = 0.0;
			short ECGmaxi = 0;

			// find max
			for(int i = 0; i < 30; i++) {
				if (rambuffer[i].asvalues.voltv.asint > ECGmax){
					ECGmax = rambuffer[i].asvalues.voltv.asint;
					ECGmaxi = i;
				}
			}
						 
			Serial.println("");
			Serial.println("peak detected!");
			Serial.print("ram n:\t");
			Serial.print(ECGmaxi);
			Serial.print("\tECG average:\t");
			Serial.print(previousECGaverage * 5.0/1024);
			Serial.print("\tVolts:\t");
			Serial.print(rambuffer[ECGmaxi].asvalues.voltv.asint * 5.0/1024);
			Serial.print("\tTime:\t");
			Serial.print(rambuffer[ECGmaxi].asvalues.timev.aslong);
			Serial.println("");
			
			if (ramn != 0) {
				Serial.print("\tDeltaTime:\t");
				Serial.print(rambuffer[ramn].asvalues.timev.aslong - rambuffer[ramn - 1].asvalues.timev.aslong);
			}
			Serial.println("");
	
			datatuple peaktuple;
	
			peaktuple.asvalues.voltv.asint = rambuffer[ECGmaxi-1].asvalues.voltv.asint - previousECGaverage;
			peaktuple.asvalues.timev.aslong = rambuffer[ECGmaxi -1].asvalues.timev.aslong;
	
			writeEEPROM(promAddr, peaktuple.asbytes, 6);
	
			promAddr = promAddr + 6;
		}
		
		delay(ms_delay);
	}
	
	times[1] = millis();
	return promAddr;
}


void writeEEPROM(int promAddr, byte* bytes, int numbytes) {
	for(int n = 0; n < numbytes; n++) {
		EEPROM.write(promAddr+n, bytes[n]);
	}
}
void readEEPROM(int promAddr, byte* bytes, int numbytes) {
	for(int n = 0; n < numbytes; n++) {
		bytes[n] = EEPROM.read(promAddr+n);
	}
}

void checkAlarm(sensorarray readings){

	bool HRalarm;
	bool RRalarm;
	bool tempalarm;
	bool alarm;

	//                        0-12mos             1yr                 2yrs              3yrs                4yrs                5yrs              6yrs                7yrs              8yrs                9yrs              10yrs             11yrs               12yrs             13yrs               14yrs             15 and up
	alarmvals age_array[] = {{93, 181, 30, 60}, {82, 156, 24, 40}, {76, 142, 24, 40}, {70, 136, 22, 34}, {65, 131, 22, 34}, {65, 131, 22, 34}, {59, 123, 18, 30}, {59, 123, 18, 30}, {52, 115, 18, 30}, {52, 115, 18, 30}, {52, 115, 18, 30},{52, 115, 18, 30}, {47, 108, 12, 16}, {47, 108, 12, 16}, {47, 108, 12,16}, {43, 104, 12, 20}}; 

	alarmvals specificalarms = age_array[eff_age];
	
	if(readings.asvalues.HR>specificalarms.upperHR || readings.asvalues.HR<specificalarms.lowerHR){
		HRalarm = true;
	}
	else{
		HRalarm = false;
	}

	if(readings.asvalues.RR>specificalarms.upperRR || readings.asvalues.RR<specificalarms.lowerRR){
		RRalarm = true;
	}
	else{
		RRalarm = false;
	}

	if(readings.asvalues.temp>uppertemp || readings.asvalues.temp<lowertemp){
		tempalarm = true;
	}
	else{
		tempalarm = false;
	}

	if((HRalarm == true && RRalarm == true) || tempalarm == true){
		alarm = true;
		digitalWrite(warningLED, HIGH);
	}
	else {
		alarm = false;
		digitalWrite(warningLED, LOW);
	}

	return alarm;
	
}
void checkAlarm2(sensorarray readings){

  bool HRalarm;
  bool RRalarm;
  bool tempalarm;
  bool alarm;
  
  if(readings.asvalues.HR> 140.0 || readings.asvalues.HR< 40.0){
    HRalarm = true;
  }
  else{
    HRalarm = false;
  }

  if(readings.asvalues.RR>35.0 || readings.asvalues.RR<10.0){
    RRalarm = true;
  }
  else{
    RRalarm = false;
  }

  if(readings.asvalues.temp>38.0 || readings.asvalues.temp<35.0){
    tempalarm = true;
  }
  else{
    tempalarm = false;
  }

  if((HRalarm == true && RRalarm == true) || tempalarm == true){
    alarm = true;
    Serial.println("alarm state has been set to true");
    digitalWrite(warningLED, HIGH);
  }
  else {
    alarm = false;
    Serial.println("alarm state has been set to false");
    digitalWrite(warningLED, LOW);
  }

  return alarm;
  
}
