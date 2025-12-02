import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';
import 'package:share_plus/share_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'package:intl/intl.dart';
import '../providers/vetri_provider.dart';

class ReportScreen extends StatelessWidget {
  const ReportScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Report Misure'),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () => _condividiPDF(context),
          ),
        ],
      ),
      body: PdfPreview(
        build: (format) => _generaPDF(context),
      ),
    );
  }

  Future<Uint8List> _generaPDF(BuildContext context) async {
    final provider = context.read<VetriProvider>();
    final pdf = pw.Document();

    // Font
    final font = await PdfGoogleFonts.nunitoRegular();
    final fontBold = await PdfGoogleFonts.nunitoBold();

    // Data
    final now = DateTime.now();
    final dateFormat = DateFormat('dd/MM/yyyy HH:mm');

    pdf.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.all(32),
        build: (context) {
          final misurePerMateriale = provider.getMisurePerMateriale();

          return [
            // Header
            pw.Header(
              level: 0,
              child: pw.Row(
                mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                children: [
                  pw.Text(
                    '📐 Metro Digitale - Report Misure',
                    style: pw.TextStyle(font: fontBold, fontSize: 20),
                  ),
                  pw.Text(
                    dateFormat.format(now),
                    style: pw.TextStyle(font: font, fontSize: 12),
                  ),
                ],
              ),
            ),
            pw.SizedBox(height: 20),

            // Riepilogo
            pw.Container(
              padding: const pw.EdgeInsets.all(16),
              decoration: pw.BoxDecoration(
                color: PdfColors.grey300,
                borderRadius: pw.BorderRadius.circular(8),
              ),
              child: pw.Column(
                crossAxisAlignment: pw.CrossAxisAlignment.start,
                children: [
                  pw.Text(
                    'RIEPILOGO',
                    style: pw.TextStyle(font: fontBold, fontSize: 14),
                  ),
                  pw.SizedBox(height: 8),
                  pw.Row(
                    mainAxisAlignment: pw.MainAxisAlignment.spaceAround,
                    children: [
                      _buildStatPDF('Misure Diverse', provider.misure.length.toString(), font, fontBold),
                      _buildStatPDF('Totale Vetri', provider.getTotaleVetri().toString(), font, fontBold),
                      _buildStatPDF('Tolleranza', '${provider.tolleranzaRaggruppamento}mm', font, fontBold),
                    ],
                  ),
                ],
              ),
            ),
            pw.SizedBox(height: 20),

            // Tabelle per materiale
            ...misurePerMateriale.entries.map((entry) {
              final materiale = entry.key;
              final misure = entry.value;

              return pw.Column(
                crossAxisAlignment: pw.CrossAxisAlignment.start,
                children: [
                  pw.Header(
                    level: 1,
                    child: pw.Text(
                      'Materiale: $materiale',
                      style: pw.TextStyle(font: fontBold, fontSize: 16),
                    ),
                  ),
                  pw.SizedBox(height: 8),
                  pw.Table.fromTextArray(
                    context: context,
                    headerStyle: pw.TextStyle(font: fontBold, fontSize: 10),
                    cellStyle: pw.TextStyle(font: font, fontSize: 9),
                    headerDecoration: const pw.BoxDecoration(color: PdfColors.grey400),
                    cellAlignment: pw.Alignment.centerLeft,
                    headers: ['#', 'Larghezza (mm)', 'Altezza (mm)', 'Gioco (mm)', 'Quantità'],
                    data: misure.asMap().entries.map((e) {
                      final idx = e.key + 1;
                      final m = e.value;
                      return [
                        idx.toString(),
                        m.larghezzaNetta.toStringAsFixed(0),
                        m.altezzaNetta.toStringAsFixed(0),
                        m.gioco.toStringAsFixed(0),
                        m.quantita.toString(),
                      ];
                    }).toList(),
                  ),
                  pw.SizedBox(height: 20),
                ],
              );
            }).toList(),

            // Footer
            pw.Spacer(),
            pw.Divider(),
            pw.Text(
              'Report generato automaticamente da Metro Digitale App',
              style: pw.TextStyle(font: font, fontSize: 8, color: PdfColors.grey700),
              textAlign: pw.TextAlign.center,
            ),
          ];
        },
      ),
    );

    return pdf.save();
  }

  pw.Widget _buildStatPDF(String label, String value, pw.Font font, pw.Font fontBold) {
    return pw.Column(
      children: [
        pw.Text(
          value,
          style: pw.TextStyle(font: fontBold, fontSize: 18),
        ),
        pw.Text(
          label,
          style: pw.TextStyle(font: font, fontSize: 10, color: PdfColors.grey700),
        ),
      ],
    );
  }

  Future<void> _condividiPDF(BuildContext context) async {
    try {
      final pdfData = await _generaPDF(context);
      final tempDir = await getTemporaryDirectory();
      final fileName = 'report_vetri_${DateFormat('yyyyMMdd_HHmmss').format(DateTime.now())}.pdf';
      final file = File('${tempDir.path}/$fileName');
      await file.writeAsBytes(pdfData);

      await Share.shareXFiles(
        [XFile(file.path)],
        text: 'Report Misure Metro Digitale',
      );
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Errore condivisione: $e')),
        );
      }
    }
  }
}
