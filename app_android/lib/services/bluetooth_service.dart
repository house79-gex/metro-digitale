import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';
import 'package:permission_handler/permission_handler.dart';
import '../models/misura_vetro.dart';

class BluetoothService with ChangeNotifier {
  static const String serviceUuid = '12345678-1234-1234-1234-123456789abc';
  static const String charRxUuid = '12345678-1234-1234-1234-123456789abe';

  BluetoothDevice? _connectedDevice;
  BluetoothCharacteristic? _rxCharacteristic;
  StreamSubscription? _scanSubscription;
  StreamSubscription? _deviceStateSubscription;
  StreamSubscription? _characteristicSubscription;

  bool _isScanning = false;
  bool get isScanning => _isScanning;
  bool get isConnected => _connectedDevice != null;
  String? get deviceName => _connectedDevice?.platformName;

  final List<BluetoothDevice> _foundDevices = [];
  List<BluetoothDevice> get foundDevices => List.unmodifiable(_foundDevices);

  // Callback per misure ricevute
  Function(MisuraVetro)? onMisuraRicevuta;

  // Richiedi permessi
  Future<bool> requestPermissions() async {
    if (defaultTargetPlatform == TargetPlatform.android) {
      final bluetoothStatus = await Permission.bluetoothScan.request();
      final locationStatus = await Permission.location.request();
      final bluetoothConnect = await Permission.bluetoothConnect.request();

      return bluetoothStatus.isGranted &&
          locationStatus.isGranted &&
          bluetoothConnect.isGranted;
    }
    return true;
  }

  // Avvia scansione
  Future<void> startScan() async {
    if (_isScanning) return;

    final hasPermissions = await requestPermissions();
    if (!hasPermissions) {
      debugPrint('Permessi Bluetooth negati');
      return;
    }

    _foundDevices.clear();
    _isScanning = true;
    notifyListeners();

    try {
      _scanSubscription = FlutterBluePlus.scanResults.listen((results) {
        for (ScanResult result in results) {
          // Cerca dispositivi Metro Digitale
          if (result.device.platformName.contains('Metro') ||
              result.advertisementData.serviceUuids.contains(Guid(serviceUuid))) {
            if (!_foundDevices.contains(result.device)) {
              _foundDevices.add(result.device);
              notifyListeners();
            }
          }
        }
      });

      await FlutterBluePlus.startScan(
        timeout: const Duration(seconds: 10),
      );

      // Auto-stop dopo timeout
      await Future.delayed(const Duration(seconds: 10));
      await stopScan();
    } catch (e) {
      debugPrint('Errore scansione: $e');
      _isScanning = false;
      notifyListeners();
    }
  }

  // Ferma scansione
  Future<void> stopScan() async {
    await FlutterBluePlus.stopScan();
    await _scanSubscription?.cancel();
    _isScanning = false;
    notifyListeners();
  }

  // Connetti a dispositivo
  Future<bool> connect(BluetoothDevice device) async {
    try {
      debugPrint('Connessione a ${device.platformName}...');
      await device.connect(timeout: const Duration(seconds: 15));

      _connectedDevice = device;

      // Monitora stato connessione
      _deviceStateSubscription = device.connectionState.listen((state) {
        if (state == BluetoothConnectionState.disconnected) {
          debugPrint('Dispositivo disconnesso');
          disconnect();
        }
      });

      // Scopri servizi
      final services = await device.discoverServices();
      for (var service in services) {
        if (service.uuid.toString().toLowerCase() == serviceUuid.toLowerCase()) {
          for (var characteristic in service.characteristics) {
            if (characteristic.uuid.toString().toLowerCase() ==
                charRxUuid.toLowerCase()) {
              _rxCharacteristic = characteristic;

              // Subscribe a notifiche
              await characteristic.setNotifyValue(true);
              _characteristicSubscription =
                  characteristic.lastValueStream.listen(_onDataReceived);

              debugPrint('Connesso e sottoscritto alle notifiche');
              notifyListeners();
              return true;
            }
          }
        }
      }

      debugPrint('Servizio o caratteristica non trovati');
      await disconnect();
      return false;
    } catch (e) {
      debugPrint('Errore connessione: $e');
      await disconnect();
      return false;
    }
  }

  // Disconnetti
  Future<void> disconnect() async {
    await _characteristicSubscription?.cancel();
    await _deviceStateSubscription?.cancel();
    await _connectedDevice?.disconnect();

    _connectedDevice = null;
    _rxCharacteristic = null;
    _characteristicSubscription = null;
    _deviceStateSubscription = null;

    notifyListeners();
  }

  // Callback dati ricevuti
  void _onDataReceived(List<int> data) {
    try {
      final jsonString = utf8.decode(data);
      debugPrint('Ricevuto: $jsonString');

      final Map<String, dynamic> json = jsonDecode(jsonString);

      // Verifica se è una misura vetro
      if (json.containsKey('larghezza_raw') && json.containsKey('altezza_raw')) {
        final misura = MisuraVetro(
          larghezzaRaw: (json['larghezza_raw'] as num).toDouble(),
          altezzaRaw: (json['altezza_raw'] as num).toDouble(),
          larghezzaNetta: (json['larghezza_netta'] as num).toDouble(),
          altezzaNetta: (json['altezza_netta'] as num).toDouble(),
          materiale: json['materiale'] as String,
          quantita: json['quantita'] as int? ?? 1,
          gioco: (json['gioco'] as num).toDouble(),
        );

        onMisuraRicevuta?.call(misura);
      }
    } catch (e) {
      debugPrint('Errore parsing dati: $e');
    }
  }

  @override
  void dispose() {
    disconnect();
    stopScan();
    super.dispose();
  }
}
