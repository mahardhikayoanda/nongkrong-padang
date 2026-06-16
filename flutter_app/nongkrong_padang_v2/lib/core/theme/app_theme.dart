import 'package:flutter/material.dart';

class AppColors {
  // Primary — hijau teal sesuai wireframe proposal
  static const primary     = Color(0xFF1B4332);
  static const primaryLight = Color(0xFF2D6A4F);
  static const accent      = Color(0xFFD4A017);  // oranye keemasan
  
  // Sentimen
  static const positif     = Color(0xFF2D6A4F);
  static const negatif     = Color(0xFFB91C1C);
  static const netral      = Color(0xFF6B7280);
  
  // Background
  static const background  = Color(0xFFF9FAFB);
  static const surface     = Color(0xFFFFFFFF);
  static const cardBg      = Color(0xFFFFFFFF);
  
  // Text
  static const textPrimary   = Color(0xFF111827);
  static const textSecondary = Color(0xFF6B7280);
  static const textHint      = Color(0xFF9CA3AF);
}

class AppTheme {
  static ThemeData get theme => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: AppColors.primary,
      primary: AppColors.primary,
      secondary: AppColors.accent,
      background: AppColors.background,
      surface: AppColors.surface,
    ),
    fontFamily: 'Poppins',
    scaffoldBackgroundColor: AppColors.background,
    
    appBarTheme: const AppBarTheme(
      backgroundColor: AppColors.primary,
      foregroundColor: Colors.white,
      elevation: 0,
      centerTitle: true,
    ),
    
    cardTheme: CardThemeData(
      color: AppColors.cardBg,
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
    ),
    
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        minimumSize: const Size(double.infinity, 52),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    ),
    
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.grey[100],
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: AppColors.primary, width: 2),
      ),
    ),
  );
}