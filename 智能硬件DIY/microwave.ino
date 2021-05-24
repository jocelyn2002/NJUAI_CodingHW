int inputPin=4;
int outputPin=5;
int ledpin = 13;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(ledpin,OUTPUT);
  pinMode(inputPin,INPUT);
  pinMode(outputPin,OUTPUT);
}

void loop() {
  unsigned int x1,x2;
  digitalWrite(outputPin, LOW);
  delayMicroseconds(2);
  digitalWrite(outputPin,HIGH);
  delayMicroseconds(10);
  digitalWrite(outputPin,LOW);
  float distance1=pulseIn(inputPin,HIGH);
  distance1=distance1/58;
  x1=distance1*100.0;
  distance1=x1/100.0;
  Serial.println(distance1);
  delay(150);
  if (distance1>=50)
  {
    digitalWrite(ledpin,HIGH);
  }
  else 
    digitalWrite(ledpin,LOW);
  // put your main code here, to run repeatedly:

}
