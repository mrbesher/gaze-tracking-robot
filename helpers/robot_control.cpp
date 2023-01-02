#include <WiFi.h>
#include <WebServer.h>

// Set the numbers
#define PIN_TEST 23


// Wifi an server setup
const char* ssid     = "besher_robot_mu";
const char* password = "robot_besher_mi";

WebServer server(80);

// Commands Config
const char* CMD_ARGUMENT = "cmd";
const char* DURATION_ARGUMENT = "dur";
const char* VELOCITY_ARGUMENT = "vel";

String FORWARD_CMD = "MF";
String BACKWARD_CMD = "MB";
String RIGHT_CMD = "TR";
String LEFT_CMD = "TL";
String PARK_CMD = "P";
String NOP_CMD = "NOP";

int DEFAULT_DURATION = 1000;
int DEFAULT_VELOCITY = 150;

void setup() {
  Serial.begin(115200);

  // setup pins
  pinMode(PIN_TEST, OUTPUT);
  digitalWrite(PIN_TEST, LOW);

  Serial.print("Setting Access Point…");
  WiFi.softAP(ssid, password);

  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);

  server.on("/", http_handler);
  server.onNotFound(HTTP_404);
  server.begin();

  park_robot();
}


void http_handler(void) {
  String cmd_arg = server.hasArg(CMD_ARGUMENT) ? server.arg(CMD_ARGUMENT) : NOP_CMD;
  int dur_arg = server.hasArg(DURATION_ARGUMENT) ? server.arg(DURATION_ARGUMENT).toInt() : DEFAULT_DURATION;
  int vel_arg = server.hasArg(VELOCITY_ARGUMENT) ? server.arg(VELOCITY_ARGUMENT).toInt() : DEFAULT_VELOCITY;

  String response = "";
  response += "Received command: " + cmd_arg + "<br>";
  response += "Duration: " + String(dur_arg) + "<br>";
  response += "Velocity: " + String(vel_arg) + "<br>";

  if (cmd_arg == NOP_CMD ||
      (cmd_arg != PARK_CMD && cmd_arg != FORWARD_CMD && cmd_arg != BACKWARD_CMD &&
       cmd_arg != RIGHT_CMD && cmd_arg != LEFT_CMD)) {
    response += "No valid command was received. The robot will not move.";
    park_robot();
    server.send(200, "text/html", response);
    return;
  } else {
    response += "Executing command...";
    if (cmd_arg == PARK_CMD) park_robot();
    else if (cmd_arg == FORWARD_CMD) move_forward(vel_arg);
    else if (cmd_arg == BACKWARD_CMD) move_backward(vel_arg);
    else if (cmd_arg == RIGHT_CMD) turn_right(vel_arg);
    else if (cmd_arg == LEFT_CMD) turn_left(vel_arg);
  }

  server.send(200, "text/html", response);

  if (dur_arg > 0)
    delay(dur_arg);

  park_robot();
}

void HTTP_404(void) {
  String response =
    "<html>"
    "<head>"
    "<title>ERROR 404</title>"
    "</head>"
    "<body>"
    "<h1>Welcome to the robot API!</h1>"
    "<p>To send a command to the robot, make a GET request to the server with the following arguments:</p>"
    "<ul>"
    "<li>cmd: The command to send to the robot. Must be one of the following:</li>"
    "<ul>"
    "<li>MF (move forward)</li>"
    "<li>MB (move backward)</li>"
    "<li>TL (turn left)</li>"
    "<li>TR (turn right)</li>"
    "<li>P (park)</li>"
    "</ul>"
    "<li>dur (optional): The duration in milliseconds to execute the command. Defaults to 1000.</li>"
    "<li>vel (optional): The velocity at which to execute the command. Defaults to 150.</li>"
    "</ul>"
    "<p>To send a request, use the following route:</p>"
    "<code>http://[server-ip]?cmd=[command]&dur=[duration]&vel=[velocity]</code>"
    "</body>"
    "</html>";

  server.send(404, "text/html", response);
}

void loop() {
  server.handleClient();
}

/**
 * Moves the robot forward at the specified velocity.
 *
 * @param velocity The velocity at which the robot should move forward.
 */
void move_forward(int velocity) {
  // Move the robot forward at the specified velocity.
  digitalWrite(PIN_TEST, HIGH);
}

/**
 * Moves the robot backward at the specified velocity.
 *
 * @param velocity The velocity at which the robot should move backward.
 */
void move_backward(int velocity) {
  // Move the robot backward at the specified velocity.
  digitalWrite(PIN_TEST, LOW);
}

/**
 * Turns the robot to the right at the specified velocity.
 *
 * @param velocity The velocity at which the robot should turn to the right.
 */
void turn_right(int velocity) {
  // Turn the robot to the right at the specified velocity.
  digitalWrite(PIN_TEST, HIGH);
}

/**
 * Turns the robot to the left at the specified velocity.
 *
 * @param velocity The velocity at which the robot should turn to the left.
 */
void turn_left(int velocity) {
  // Turn the robot to the left at the specified velocity.
  digitalWrite(PIN_TEST, LOW);
}

/**
 * Stops the robot.
 */
void park_robot() {
  // Stop the robot.
  if (digitalRead(PIN_TEST) == LOW) {
    digitalWrite(PIN_TEST, HIGH);
    return;
  }
  digitalWrite(PIN_TEST, LOW);
}
