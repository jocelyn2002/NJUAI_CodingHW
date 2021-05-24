int ledPin = 9;
void setup() {
  // put your setup code here, to run once:
  pinMode(ledPin,OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  //for(int fadeValue = 0;fadeValue<=255;fadeValue+=5){
   // analogWrite(ledPin,fadeValue);
  //}
  //for(int fadeValue = 255;fadeValue >= 0;fadeValue -= 5){
    //analogWrite(ledPin,fadeValue);
  //}
  for(int i=0;i<=50;i++)
  {
    digitalWrite(ledPin,1); 
    delay(i/10);
    digitalWrite(ledPin,0);
    delay((5-i/10));
  }
  for(int i=50;i>=0;i--)
  {
    digitalWrite(ledPin,1); 
    delay(i/10);
    digitalWrite(ledPin,0);
    delay((5-i/10));
  }
}
