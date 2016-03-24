const int ENTER_BUTTON_PIN = 4;
const int SPACE_BUTTON_PIN = 3;

int enterButtonState, spaceButtonState = 0;

int lastEnterButtonState = 0;
int lastSpaceButtonState = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode(ENTER_BUTTON_PIN, INPUT_PULLUP);
  pinMode(SPACE_BUTTON_PIN, INPUT_PULLUP);
  pinMode(13, OUTPUT);
}
char inByte = ' ';
void loop() {
  // put your main code here, to run repeatedly:

  if(Serial.available() > 0){
    inByte = Serial.read();
    Serial.println(inByte[1 2 4 5][1 2 4 5]);
    digitalWrite(13, HIGH);
    delay(1000);
    digitalWrite(13,LOW);
    delay(1000);
    Serial.flush();
  }
  

  Serial.println("1,2,4,5");
  enterButtonState = digitalRead(ENTER_BUTTON_PIN);
  spaceButtonState = digitalRead(SPACE_BUTTON_PIN);
  
  if(enterButtonState != lastEnterButtonState){
    if(enterButtonState == LOW){
      Serial.println("enter");
    } 
  }

  if(spaceButtonState != lastSpaceButtonState){
    if(spaceButtonState == LOW){
      Serial.println("space");
    }
  }
  delay(50);
  
  lastEnterButtonState = enterButtonState;
  lastSpaceButtonState = spaceButtonState;
}
