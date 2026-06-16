import 'package:flutter/material.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({Key? key}) : super(key: key);

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  // TODO: Hubungkan dengan state management (Provider/Bloc/Riverpod) untuk fetch dari API backend/riwayat

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Riwayat Kunjungan',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    // Simulasi data kosong atau sedang loading
    // Nanti ganti dengan kondisi data sesungguhnya dari API
    bool isLoading = false; 
    bool hasData = true; // Ubah ke true untuk melihat dummy UI

    if (isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (!hasData) {
      return const Center(
        child: Text('Belum ada riwayat kunjungan tempat.'),
      );
    }

    return ListView.builder(
      itemCount: 5, // Dummy jumlah data
      padding: const EdgeInsets.all(16.0),
      itemBuilder: (context, index) {
        return Card(
          elevation: 2,
          margin: const EdgeInsets.only(bottom: 12.0),
          child: ListTile(
            leading: ClipRRect(
              borderRadius: BorderRadius.circular(8.0),
              child: Container(
                width: 50,
                height: 50,
                color: Colors.grey[300],
                child: const Icon(Icons.storefront, color: Colors.grey),
              ),
            ),
            title: Text('Nama Cafe / Tempat Nongkrong ${index + 1}', 
                style: const TextStyle(fontWeight: FontWeight.bold)),
            subtitle: const Text('Dikunjungi: Baru saja'),
            trailing: const Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () {
              // TODO: Navigasi ke DetailScreen
              // Navigator.pushNamed(context, '/detail', arguments: placeId);
            },
          ),
        );
      },
    );
  }
}