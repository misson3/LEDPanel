//Jan25, 2020, ms
//Feb09, 2020, ms  # 3 bus stops
//Feb15, 2020, ms  # add long line to connector line.  change rules
//Feb23, 2020, ms  # display 1 and 2, under line them
// get json data from serial
// display info on the LED matrix (32x64)

#include <ArduinoJson.h>
#include <RGBmatrixPanel.h>

#define CLK  8   // USE THIS ON ADAFRUIT METRO M0, etc.
//#define CLK A4 // USE THIS ON METRO M4 (not M0)
//#define CLK 11 // USE THIS ON ARDUINO MEGA
#define OE   9
#define LAT 10
#define A   A0
#define B   A1
#define C   A2
#define D   A3
RGBmatrixPanel matrix(A, B, C, D, CLK, LAT, OE, false, 64);

// test json
// {'bus': [1, 'stopid', 'busnum', '01 min', 'G', '11 mins', 'G', '17 mins', 'G']}
// {'bus': [2, 'stopid', 'busnum', ['01', 'G', '11', 'G', '17', 'G'], // the bus stop
//                              ['Ar', 'G', '08', 'Y', '10', 'R'], // aft Yew tee
//                              ['Le', 'O', '12', 'G', '19', 'Y'], // aft the bus stop
//                              ['dash3', 'shash2']
// {'bus': [2, 'BusNow', 'DP1', ['L1', 'G', 'L2', 'G', 'L3', 'G'], ['B1', 'G', 'B2', 'Y', 'B3', 'R'], ['A1', 'O', 'A2', 'G', 'A3', 'Y'], [3,3]]}
// {'bus': [2, 'BusNow', 'DP2', ['01', 'G', '08', 'G', '12', 'G'], ['Ar', 'G', '15', 'Y', '18', 'R'], ['03', 'O', '09', 'G', '14', 'Y'], [3,1]]}
// {"haya2":[1, "+1879d", "251571.33", "x1000 km"]}
// {"red":[1, "Halting...", "Bye."]}

// {'route': [1, ['RouteNow', 'r1'], [min, summary], [min, summary], [min, summary], time]}
// {'route': [1, ['RouteNow', 'r1'], [min, summary], [99, NA], [99, NA], time]}


void setup() {
  // Serial
  Serial.begin(9600);
  // LED matrix
  matrix.begin();
  // draw a pixel in solid white
  matrix.drawPixel(0, 0, matrix.Color333(7, 7, 7));
  delay(500);
  // fill the screen with 'black'
  matrix.fillScreen(matrix.Color333(0, 0, 0));
  // size, wrap
  matrix.setTextSize(1);     // size 1 == 8 pixels high
  matrix.setTextWrap(false); // Don't wrap at end of line - will do ourselves
}


void loop() {
  if (Serial.available() > 0) {
    String str = Serial.readStringUntil('\n');
    Serial.println("SSS + " + str);

    const size_t capacity = 600;
    DynamicJsonDocument doc(capacity);
    DeserializationError err = deserializeJson(doc, str);
    Serial.printf("DeserializationError:%s\n", err.c_str());

    // clear matrix
    matrix.fillScreen(matrix.Color333(0, 0, 0));

    // not very beautiful here...
    // some will be undef
    // if this is python, it will give an error
    int bus = doc["bus"][0];
    String disp = doc["bus"][2];  // ------------------- Feb23
    int haya2 = doc["haya2"][0];
    int red = doc["red"][0];
    int route = doc["route"][0];  // ----- Sep06, 2020

    if (bus == 1) {
      Serial.println("json for bus arrival");
      displayBus(doc);
    } else if (bus == 2) {
      Serial.println("json for bus arrival 2");
      displayBus2(doc);
      underline(disp);  // ---------------------------- Feb23
    } else if (haya2 == 1) {
      Serial.println("json for haya2");
      displayHaya2(doc);
    } else if (red == 1) {
      Serial.println("red.  halting message");
      displayRed(doc);
    } else if (route == 1) {  // ----- Sep06, 2020
      Serial.println("json for routes with google Directions API");
      displayRoute(doc);
    } else {
      Serial.println("not bus info");
      displayNoInfo();
    }
  }
}


/*
   my Functions
*/
void displayNoInfo() {
  // display one line
  matrix.setCursor(3, 12);
  matrix.setTextColor(matrix.Color333(1, 1, 1)); //
  matrix.println("No Info...");
}


void displayBus(DynamicJsonDocument doc) {
  // parse json
  String bus_stop = doc["bus"][1];
  String bus_line = doc["bus"][2];
  String next_bus_1 = doc["bus"][3];
  String next_bus_2 = doc["bus"][5];
  String next_bus_3 = doc["bus"][7];
  String next_bus_1_col = doc["bus"][4];
  String next_bus_2_col = doc["bus"][6];
  String next_bus_3_col = doc["bus"][8];
  // debug
  Serial.println("Line 1: " + bus_stop + "   " + bus_line);
  Serial.println("Line 2: " + next_bus_1 + "  " + next_bus_1_col);
  Serial.println("Line 3: " + next_bus_2 + "  " + next_bus_2_col);
  Serial.println("Line 4: " + next_bus_3 + "  " + next_bus_3_col);
  // display
  // Line 1-1
  matrix.setCursor(1, 0);
  matrix.setTextColor(matrix.Color333(3, 3, 3)); // bus stop, white
  matrix.println(bus_stop);
  // Line 1-2
  matrix.setCursor(43, 0);
  matrix.setTextColor(matrix.Color333(3, 0, 6)); // bus line num, red-purple
  matrix.println(bus_line);
  // Line 2
  matrix.setCursor(3, 8);
  matrix.setTextColor(statusColor(next_bus_1_col));
  matrix.println(next_bus_1);
  // Line 3
  matrix.setCursor(3, 16);
  matrix.setTextColor(statusColor(next_bus_2_col));
  matrix.println(next_bus_2);
  // Line 4
  matrix.setCursor(3, 24);
  matrix.setTextColor(statusColor(next_bus_3_col));
  matrix.println(next_bus_3);
}


void displayBus2(DynamicJsonDocument doc) {
  // parse json
  // line 1 elements
  String bus_stop = doc["bus"][1];
  String bus_line = doc["bus"][2];

  // line 2 elements: bus 1 in 3 stops
  String bef_b1 = doc["bus"][4][0];
  String len_b1 = doc["bus"][3][0]; //
  String aft_b1 = doc["bus"][5][0];
  String bef_b1c = doc["bus"][4][1];
  String len_b1c = doc["bus"][3][1]; //
  String aft_b1c = doc["bus"][5][1];
  // line 3 elements: bus 2 in 3 stops
  String bef_b2 = doc["bus"][4][2];
  String len_b2 = doc["bus"][3][2]; //
  String aft_b2 = doc["bus"][5][2];
  String bef_b2c = doc["bus"][4][3];
  String len_b2c = doc["bus"][3][3]; //
  String aft_b2c = doc["bus"][5][3];
  // line 4 elements: bus 3 in 3 stops
  String bef_b3 = doc["bus"][4][4];
  String len_b3 = doc["bus"][3][4]; //
  String aft_b3 = doc["bus"][5][4];
  String bef_b3c = doc["bus"][4][5];
  String len_b3c = doc["bus"][3][5]; //
  String aft_b3c = doc["bus"][5][5];

  // dash or slash.  connector char
  int d_or_s_1 = doc["bus"][6][0];
  int d_or_s_2 = doc["bus"][6][1];

  // debug
  Serial.println("Line 1: " + bus_stop + "   " + bus_line);
  Serial.println("Line 2: " + aft_b1 + "-" + aft_b1c + ", " + len_b1 + "-" + len_b1c + ", " + bef_b1 + "-" + bef_b1c);
  Serial.println("Line 3: " + aft_b2 + "-" + aft_b2c + ", " + len_b2 + "-" + len_b2c + ", " + bef_b2 + "-" + bef_b2c);
  Serial.println("Line 4: " + aft_b3 + "-" + aft_b3c + ", " + len_b3 + "-" + len_b3c + ", " + bef_b3 + "-" + bef_b3c);
  // display
  // Line 1-1
  matrix.setCursor(1, 0);
  matrix.setTextColor(matrix.Color333(3, 3, 3)); // bus stop, white
  matrix.println(bus_stop);
  // Line 1-2
  matrix.setCursor(43, 0);
  matrix.setTextColor(matrix.Color333(3, 0, 6)); // bus line num, red-purple
  matrix.println(bus_line);

  // Line 2
  matrix.setCursor(6, 8);
  matrix.setTextColor(statusColor(aft_b1c));
  matrix.println(aft_b1);
  matrix.setCursor(26, 8);
  matrix.setTextColor(statusColor(len_b1c));
  matrix.println(len_b1);
  matrix.setCursor(46, 8);
  matrix.setTextColor(statusColor(bef_b1c));
  matrix.println(bef_b1);
  // Line 3
  matrix.setCursor(6, 16);
  matrix.setTextColor(statusColor(aft_b2c));
  matrix.println(aft_b2);
  matrix.setCursor(26, 16);
  matrix.setTextColor(statusColor(len_b2c));
  matrix.println(len_b2);
  matrix.setCursor(46, 16);
  matrix.setTextColor(statusColor(bef_b2c));
  matrix.println(bef_b2);
  // Line 4
  matrix.setCursor(6, 24);
  matrix.setTextColor(statusColor(aft_b3c));
  matrix.println(aft_b3);
  matrix.setCursor(26, 24);
  matrix.setTextColor(statusColor(len_b3c));
  matrix.println(len_b3);
  matrix.setCursor(46, 24);
  matrix.setTextColor(statusColor(bef_b3c));
  matrix.println(bef_b3);

  // write dash or slash
  dash_and_slash(d_or_s_1, d_or_s_2);
}


////////////////////////////////////////////////////////////////////////////////////////
void dash_and_slash(int ds1, int ds2) {
  // left hand side
  if (ds1 == 3) {
    matrix.setCursor(19, 8);
    matrix.setTextColor(matrix.Color333(1, 1, 1));
    matrix.println('-');
    matrix.setCursor(19, 16);
    matrix.setTextColor(matrix.Color333(1, 1, 1));
    matrix.println('-');
    matrix.setCursor(19, 24);
    matrix.setTextColor(matrix.Color333(1, 1, 1));
    matrix.println('-');
  }else if (ds1 == 2) {
    matrix.setCursor(19, 12);
    matrix.setTextColor(matrix.Color333(1, 1, 1));
    matrix.println('/');
    matrix.setCursor(19, 20);
    matrix.setTextColor(matrix.Color333(1, 1, 1));
    matrix.println('/');
  }else if (ds1 == 1) {
    matrix.drawLine(19, 27, 23, 11, matrix.Color333(1, 1, 1));
    //matrix.drawPixel(19, 27, matrix.Color333(1, 0, 0));
    //matrix.drawPixel(23, 11, matrix.Color333(0, 1, 0));
  }

  // right hand side
  if (ds2 == 3) {
    matrix.setCursor(39, 8);
    matrix.setTextColor(matrix.Color333(1, 1, 1));
    matrix.println('-');
    matrix.setCursor(39, 16);
    matrix.setTextColor(matrix.Color333(1, 1, 1));
    matrix.println('-');
    matrix.setCursor(39, 24);
    matrix.setTextColor(matrix.Color333(1, 1, 1));
    matrix.println('-');
  }else if (ds2 == 2) {
    matrix.setCursor(39, 12);
    matrix.setTextColor(matrix.Color333(1, 1, 1));
    matrix.println('/');
    matrix.setCursor(39, 20);
    matrix.setTextColor(matrix.Color333(1, 1, 1));
    matrix.println('/');
  }else if (ds2 == 1) {
    matrix.drawLine(39, 27, 43, 11, matrix.Color333(1, 1, 1));
    //matrix.drawPixel(39, 27, matrix.Color333(1, 0, 0));
    //matrix.drawPixel(43, 11, matrix.Color333(0, 1, 0));
  }
}


void underline(String disp){
  if (disp.equals("DP1")){
    // center
    matrix.drawLine(26, 31, 36, 31, matrix.Color333(7, 0, 7));
  } else if (disp.equals("DP2")) {
    // left
    matrix.drawLine(6, 31, 16, 31, matrix.Color333(7, 0, 7));
  }
}


/////////////////////////////////////////////////////////////////////////////////
void displayHaya2(DynamicJsonDocument doc) {
  // parse json
  String haya2_days = doc["haya2"][1];
  String haya2_d2e = doc["haya2"][2];  // distance to Earth
  String haya2_unit_km = doc["haya2"][3];  // unit for distance
  // debug
  Serial.println("Line 1: Haya2 web");
  Serial.println("Line 2: " + haya2_days);
  Serial.println("Line 3: " + haya2_d2e);
  Serial.println("Line 4: " + haya2_unit_km);
  // display
  // Line 1-1
  matrix.setCursor(1, 0);
  matrix.setTextColor(matrix.Color333(0, 4, 4)); // Haya2
  matrix.println("Hayabusa2");
  // Line 2
  matrix.setCursor(7, 8);
  matrix.setTextColor(matrix.Color333(3, 3, 3)); // days since launch
  matrix.println(haya2_days);
  // Line 3
  matrix.setCursor(7, 16);
  matrix.setTextColor(matrix.Color333(6, 1, 0));
  matrix.println(haya2_d2e);  // in km
  // Line 4
  matrix.setCursor(16, 24);
  matrix.setTextColor(matrix.Color333(6, 1, 0));
  matrix.println(haya2_unit_km);
  // Line 4
  //matrix.setCursor(2, 24);
  //matrix.setTextColor(matrix.Color333(3,0,3));
  //matrix.println(haya2_rwrt);  // light time to take round trip to haya2
}


void displayRed(DynamicJsonDocument doc) {
  // parse json
  String str1 = doc["red"][1];
  String str2 = doc["red"][2];
  // debug
  Serial.println("Line 1: ");
  Serial.println("Line 2: " + str1);
  Serial.println("Line 3: " + str2);
  Serial.println("Line 4: ");
  // display
  // Line 1
  // Line 2
  matrix.setCursor(3, 8);
  matrix.setTextColor(matrix.Color333(3, 0, 0)); // days since launch
  matrix.println(str1);
  // Line 3
  matrix.setCursor(28, 19);
  matrix.setTextColor(matrix.Color333(0, 3, 0));
  matrix.println(str2);
  // Line 4

  // wait for 10 seconds
  delay(10000);
  // then erase display
  matrix.fillScreen(matrix.Color333(0, 0, 0));
}


void displayRoute(DynamicJsonDocument doc) {
  // {'route': [1, ['RouteNow', 'r1'], [min, summary], [min, summary], [min, summary], time]}
  String banner1 = doc['route'][1][0];  // RouteNow
  String banner2 = doc['route'][1][1];  // r1
  String time1 = doc['route'][2][0];
  // String summary1 = doc['route'][2][1];
  String time2 = doc['route'][3][0];
  // String summary2 = doc['route'][3][0];
  String time3 = doc['route'][4][0];
  // String summary3 = doc['route'][4][0];
  String ts = doc['route'][5];  // time

  // display
  // Line 1-1
  matrix.setCursor(1, 0);
  matrix.setTextColor(matrix.Color333(3, 3, 3)); // bus stop, white
  matrix.println(banner1);
  // Line 1-2
  matrix.setCursor(51, 0);
  matrix.setTextColor(matrix.Color333(3, 0, 6)); // bus line num, red-purple
  matrix.println(banner2);

  // try bigger size
  matrix.setTextSize(2);
  matrix.setCursor(6, 8);
  matrix.setTextColor(matrix.Color333(0, 5, 0));
  matrix.println('21, 25, 26')
}


uint16_t statusColor(String col) {
  if (col == "G") {
    return matrix.Color333(0, 5, 0); // Green
  } else if (col == "Y") {
    return matrix.Color333(3, 3, 0); // Yellow
  } else if (col == "R") {
    return matrix.Color333(5, 0, 0); // Red
  } else if (col == "O") {
    return matrix.Color333(6, 1, 0); // Orange for Left...
  } else {
    return matrix.Color333(1, 1, 1); // weak white for now
  }
}

