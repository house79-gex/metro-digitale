import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/vetri_provider.dart';
import '../services/bluetooth_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Impostazioni'),
      ),
      body: ListView(
        children: [
          _buildBluetoothSection(),
          const Divider(),
          _buildMisureSection(),
          const Divider(),
          _buildInfoSection(),
        ],
      ),
    );
  }

  Widget _buildBluetoothSection() {
    return Consumer<BluetoothService>(
      builder: (context, btService, _) {
        return Column(
          children: [
            ListTile(
              leading: const Icon(Icons.bluetooth),
              title: const Text('Bluetooth'),
              subtitle: Text(
                btService.isConnected 
                    ? 'Connesso: ${btService.deviceName}' 
                    : 'Non connesso',
              ),
              trailing: btService.isConnected
                  ? ElevatedButton(
                      onPressed: () async {
                        await btService.disconnect();
                        if (mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Disconnesso')),
                          );
                        }
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                      ),
                      child: const Text('Disconnetti'),
                    )
                  : ElevatedButton(
                      onPressed: () async {
                        await btService.startScan();
                      },
                      child: const Text('Cerca'),
                    ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildMisureSection() {
    return Consumer<VetriProvider>(
      builder: (context, provider, _) {
        return Column(
          children: [
            ListTile(
              leading: const Icon(Icons.straighten),
              title: const Text('Tolleranza Raggruppamento'),
              subtitle: Text('${provider.tolleranzaRaggruppamento.toStringAsFixed(1)} mm'),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Slider(
                value: provider.tolleranzaRaggruppamento,
                min: 0.5,
                max: 5.0,
                divisions: 9,
                label: '${provider.tolleranzaRaggruppamento.toStringAsFixed(1)} mm',
                onChanged: (value) {
                  provider.setTolleranza(value);
                },
              ),
            ),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: Text(
                'Misure entro questa tolleranza vengono raggruppate automaticamente',
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildInfoSection() {
    return Column(
      children: [
        const ListTile(
          leading: Icon(Icons.info),
          title: Text('Metro Digitale App'),
          subtitle: Text('Versione 1.0.0'),
        ),
        ListTile(
          leading: const Icon(Icons.description),
          title: const Text('Funzionalità'),
          subtitle: const Text(
            '• Ricezione misure via Bluetooth\n'
            '• Raggruppamento intelligente\n'
            '• Generazione report PDF\n'
            '• Condivisione report',
          ),
        ),
      ],
    );
  }
}
