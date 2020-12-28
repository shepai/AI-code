#include <Adafruit_NeoPixel.h>
#define PIN 6
Adafruit_NeoPixel strip = Adafruit_NeoPixel(64, PIN, NEO_GRB + NEO_KHZ800);

int setPoint = 55;

void setup() {
  strip.begin();
  strip.setBrightness(64);
  pinMode(13,OUTPUT);
  
  strip.show(); // Initialize all pixels to 'off'
  Serial.begin(9600);  // initialize serial communications at 9600 bps
}

void writeEYE(String s)
{

  strip.clear(); //clear
  
  int start[8]={56,55,40,39,24,23,8,7};
  //RRRRRRRRBBBBBBBBRRRRRRRRBBBBBBBBRRRRRRRRBBBBBBBBRRRRRRRRBBBBBBBB
  
  for(int j=0;j<8;j++){
    String s1=s.substring(j*8,(j*8)+8);
    int current=j;
    boolean row=true;
  for(int i=0;i<8;i++) //set all pixel colours
  {
     char pixel=s1.charAt(i);
     //Serial.println(start[i]+current);
     if(pixel=='R')
     {
      strip.setPixelColor(start[i]+current, 255, 0, 0); 
     }else if(pixel=='W')
     {
      strip.setPixelColor(start[i]+current, 255, 255, 255); 
     }else if(pixel=='B')
     {
      strip.setPixelColor(start[i]+current, 0, 0, 255); 
     }
     row=not(row);
     if(row){current=j;}else{current=-j;}
     
  }}
  //*/
  strip.show(); //show it to the user
}
String readString="";
void loop() {
  // put your main code here, to run repeatedly:
  
  
  while(!Serial.available()) {}
  // serial read section
  while (Serial.available())
  {
    if (Serial.available() >0)
    {
      char c = Serial.read();  //gets one byte from serial buffer
      readString += c; //makes the string readString
    }
  }
  
  
  if (readString.length()==64)
  {
    
    digitalWrite(13,HIGH);
    writeEYE(readString); //write to eye
    Serial.println(readString);
    readString="";
  }

  delay(500);
  digitalWrite(13,LOW);
}
