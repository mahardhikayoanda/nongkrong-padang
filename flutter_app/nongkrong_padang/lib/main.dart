import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'core/theme/app_theme.dart';
import 'core/utils/storage_helper.dart';
import 'presentation/screens/onboarding/onboarding_screen.dart';
import 'presentation/screens/auth/login_screen.dart';
import 'presentation/screens/auth/register_screen.dart';
import 'presentation/screens/home/home_screen.dart';
import 'presentation/screens/detail/detail_screen.dart';
import 'presentation/screens/search/search_screen.dart';
import 'presentation/screens/profile/profile_screen.dart';
import 'presentation/screens/favorites/favorites_screen.dart';
import 'presentation/screens/admin/admin_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final isLoggedIn = await StorageHelper.isLoggedIn();
  runApp(NongkrongPadangApp(isLoggedIn: isLoggedIn));
}

class NongkrongPadangApp extends StatelessWidget {
  final bool isLoggedIn;
  const NongkrongPadangApp({super.key, required this.isLoggedIn});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Nongkrong Padang',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.theme,
      routerConfig: _router(isLoggedIn),
    );
  }

  GoRouter _router(bool isLoggedIn) => GoRouter(
    initialLocation: isLoggedIn ? '/home' : '/',
    routes: [
      GoRoute(path: '/',        builder: (_, __) => const OnboardingScreen()),
      GoRoute(path: '/login',   builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/register',builder: (_, __) => const RegisterScreen()),
      GoRoute(path: '/home',    builder: (_, __) => const HomeScreen()),
      GoRoute(
        path: '/detail/:id',
        builder: (_, state) => DetailScreen(
          idTempat: state.pathParameters['id']!
        ),
      ),
      GoRoute(path: '/search',    builder: (_, __) => const SearchScreen()),
      GoRoute(path: '/profile',   builder: (_, __) => const ProfileScreen()),
      GoRoute(path: '/favorites', builder: (_, __) => const FavoritesScreen()),
      GoRoute(path: '/admin',     builder: (_, __) => const AdminScreen()),
    ],
  );
}