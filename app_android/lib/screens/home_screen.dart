import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/vetri_provider.dart';
import '../services/bluetooth_service.dart';
import 'report_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    // Setup callback per misure ricevute
    final btService = context.read<BluetoothService>();
    final vetriProvider = context.read<VetriProvider>();
    btService.onMisuraRicevuta = (misura) {
      vetriProvider.aggiungiMisura(misura);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Misura ricevuta: ${misura.larghezzaNetta.toStringAsFixed(0)} x ${misura.altezzaNetta.toStringAsFixed(0)} mm'),
          duration: const Duration(seconds: 2),
        ),
      );
    };
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📐 Metro Digitale'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const SettingsScreen()),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          _buildBluetoothStatus(),
          _buildStatsCard(),
          const Divider(),
          Expanded(child: _buildMisureList()),
        ],
      ),
      floatingActionButton: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          FloatingActionButton(
            heroTag: 'report',
            onPressed: _generaReport,
            tooltip: 'Genera Report',
            child: const Icon(Icons.picture_as_pdf),
          ),
          const SizedBox(height: 16),
          FloatingActionButton(
            heroTag: 'clear',
            onPressed: _svuotaMisure,
            backgroundColor: Colors.red,
            tooltip: 'Svuota Lista',
            child: const Icon(Icons.delete_sweep),
          ),
        ],
      ),
    );
  }

  Widget _buildBluetoothStatus() {
    return Consumer<BluetoothService>(
      builder: (context, btService, _) {
        return Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          color: btService.isConnected ? Colors.green.shade100 : Colors.red.shade100,
          child: Row(
            children: [
              Icon(
                btService.isConnected ? Icons.bluetooth_connected : Icons.bluetooth_disabled,
                color: btService.isConnected ? Colors.green : Colors.red,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  btService.isConnected
                      ? 'Connesso: ${btService.deviceName ?? "Dispositivo"}'
                      : 'Non connesso',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
              if (!btService.isConnected)
                ElevatedButton(
                  onPressed: _showDeviceList,
                  child: const Text('Connetti'),
                ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildStatsCard() {
    return Consumer<VetriProvider>(
      builder: (context, provider, _) {
        return Card(
          margin: const EdgeInsets.all(16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatItem('Misure', provider.misure.length.toString()),
                _buildStatItem('Totale Vetri', provider.getTotaleVetri().toString()),
                _buildStatItem('Tolleranza', '${provider.tolleranzaRaggruppamento.toStringAsFixed(1)} mm'),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildStatItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        Text(
          label,
          style: TextStyle(fontSize: 12, color: Colors.grey[600]),
        ),
      ],
    );
  }

  Widget _buildMisureList() {
    return Consumer<VetriProvider>(
      builder: (context, provider, _) {
        if (provider.misure.isEmpty) {
          return const Center(
            child: Text(
              'Nessuna misura.\nConnetti il Metro Digitale e inizia a misurare.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
          );
        }

        return ListView.builder(
          itemCount: provider.misure.length,
          itemBuilder: (context, index) {
            final misura = provider.misure[index];
            return Card(
              margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: ListTile(
                leading: CircleAvatar(
                  child: Text('${index + 1}'),
                ),
                title: Text(
                  'L: ${misura.larghezzaNetta.toStringAsFixed(0)} mm × H: ${misura.altezzaNetta.toStringAsFixed(0)} mm',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                subtitle: Text(
                  'Materiale: ${misura.materiale} | Gioco: ${misura.gioco.toStringAsFixed(0)}mm',
                ),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.remove),
                      onPressed: () {
                        if (misura.quantita > 1) {
                          provider.modificaQuantita(index, misura.quantita - 1);
                        }
                      },
                    ),
                    Text(
                      '${misura.quantita}',
                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    IconButton(
                      icon: const Icon(Icons.add),
                      onPressed: () {
                        provider.modificaQuantita(index, misura.quantita + 1);
                      },
                    ),
                    IconButton(
                      icon: const Icon(Icons.delete, color: Colors.red),
                      onPressed: () => provider.rimuoviMisura(index),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  void _showDeviceList() async {
    final btService = context.read<BluetoothService>();
    await btService.startScan();

    if (!mounted) return;

    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Consumer<BluetoothService>(
          builder: (context, service, _) {
            return Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    'Dispositivi Trovati',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                ),
                if (service.isScanning) const LinearProgressIndicator(),
                Expanded(
                  child: ListView.builder(
                    itemCount: service.foundDevices.length,
                    itemBuilder: (context, index) {
                      final device = service.foundDevices[index];
                      return ListTile(
                        leading: const Icon(Icons.bluetooth),
                        title: Text(device.platformName.isNotEmpty ? device.platformName : 'Dispositivo Sconosciuto'),
                        subtitle: Text(device.remoteId.toString()),
                        trailing: ElevatedButton(
                          onPressed: () async {
                            Navigator.pop(context);
                            final success = await service.connect(device);
                            if (success && mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Connesso!')),
                              );
                            }
                          },
                          child: const Text('Connetti'),
                        ),
                      );
                    },
                  ),
                ),
              ],
            );
          },
        );
      },
    );
  }

  void _generaReport() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const ReportScreen()),
    );
  }

  void _svuotaMisure() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Conferma'),
        content: const Text('Vuoi cancellare tutte le misure?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Annulla'),
          ),
          TextButton(
            onPressed: () {
              context.read<VetriProvider>().svuotaMisure();
              Navigator.pop(context);
            },
            child: const Text('Conferma', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}
