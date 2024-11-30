import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

final ThemeData pinkTheme = ThemeData(
  colorScheme: ColorScheme.fromSeed(
    seedColor: Color(0xFFE37EA6),
    brightness: Brightness.light,
  ),
  fontFamily:  GoogleFonts.lato().fontFamily,
  appBarTheme: AppBarTheme(
    backgroundColor: Color(0xFFF4AAC9),
    foregroundColor: Color(0xFF1F55B3), // Adjust text color for contrast
  ),
  buttonTheme: ButtonThemeData(
    buttonColor: Color(0xFFED83B0),
    textTheme: ButtonTextTheme.primary,
  ),
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: Color(0xFFF4AAC9),
      foregroundColor: Colors.white,
    ),
  ),
  outlinedButtonTheme: OutlinedButtonThemeData(
    style: OutlinedButton.styleFrom(
      side: BorderSide(color: Colors.pink),
      foregroundColor: Colors.pink,
    ),
  ),
);