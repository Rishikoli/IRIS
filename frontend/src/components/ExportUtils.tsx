import jsPDF from 'jspdf';
import 'jspdf-autotable';
import * as XLSX from 'xlsx';

interface ExportData {
  summary: any;
  trends: any[];
  sectors: any[];
  regions: any[];
}

export class ExportUtils {
  static exportToPDF(data: ExportData, filename: string = 'iris-analytics-report.pdf') {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.width;
    
    // Title
    doc.setFontSize(20);
    doc.text('IRIS RegTech Platform - Analytics Report', pageWidth / 2, 20, { align: 'center' });
    
    // Date
    doc.setFontSize(10);
    doc.text(`Generated on: ${new Date().toLocaleDateString()}`, pageWidth / 2, 30, { align: 'center' });
    
    let yPosition = 50;
    
    // Platform Overview
    doc.setFontSize(16);
    doc.text('Platform Overview', 20, yPosition);
    yPosition += 10;
    
    const overviewData = [
      ['Total Tips Analyzed', data.summary?.overview?.total_tips_analyzed?.toLocaleString() || '0'],
      ['Documents Verified', data.summary?.overview?.total_documents_verified?.toLocaleString() || '0'],
      ['Fraud Chains Detected', data.summary?.overview?.total_fraud_chains_detected?.toString() || '0'],
      ['Human Reviews', data.summary?.overview?.total_human_reviews?.toString() || '0'],
      ['High Risk Percentage', `${data.summary?.risk_analysis?.high_risk_percentage || 0}%`],
      ['AI Confidence', `${data.summary?.risk_analysis?.avg_ai_confidence || 0}%`]
    ];
    
    (doc as any).autoTable({
      startY: yPosition,
      head: [['Metric', 'Value']],
      body: overviewData,
      theme: 'grid',
      headStyles: { fillColor: [59, 130, 246] }
    });
    
    yPosition = (doc as any).lastAutoTable.finalY + 20;
    
    // Sector Analysis
    if (yPosition > 250) {
      doc.addPage();
      yPosition = 20;
    }
    
    doc.setFontSize(16);
    doc.text('Top Risk Sectors', 20, yPosition);
    yPosition += 10;
    
    const sectorData = data.sectors.slice(0, 10).map(sector => [
      sector.sector,
      sector.total_cases.toString(),
      sector.high_risk_cases.toString(),
      `${sector.high_risk_percentage}%`,
      sector.risk_level
    ]);
    
    (doc as any).autoTable({
      startY: yPosition,
      head: [['Sector', 'Total Cases', 'High Risk', 'Risk %', 'Level']],
      body: sectorData,
      theme: 'grid',
      headStyles: { fillColor: [59, 130, 246] }
    });
    
    yPosition = (doc as any).lastAutoTable.finalY + 20;
    
    // Regional Analysis
    if (yPosition > 200) {
      doc.addPage();
      yPosition = 20;
    }
    
    doc.setFontSize(16);
    doc.text('Regional Analysis', 20, yPosition);
    yPosition += 10;
    
    const regionData = data.regions.slice(0, 10).map(region => [
      region.region,
      region.total_cases.toString(),
      region.high_risk_cases.toString(),
      `${region.high_risk_percentage}%`,
      region.population_category
    ]);
    
    (doc as any).autoTable({
      startY: yPosition,
      head: [['Region', 'Total Cases', 'High Risk', 'Risk %', 'Category']],
      body: regionData,
      theme: 'grid',
      headStyles: { fillColor: [59, 130, 246] }
    });
    
    doc.save(filename);
  }
  
  static exportToExcel(data: ExportData, filename: string = 'iris-analytics-report.xlsx') {
    const workbook = XLSX.utils.book_new();
    
    // Overview Sheet
    const overviewData = [
      ['Metric', 'Value'],
      ['Total Tips Analyzed', data.summary?.overview?.total_tips_analyzed || 0],
      ['Documents Verified', data.summary?.overview?.total_documents_verified || 0],
      ['Fraud Chains Detected', data.summary?.overview?.total_fraud_chains_detected || 0],
      ['Human Reviews', data.summary?.overview?.total_human_reviews || 0],
      ['High Risk Percentage', `${data.summary?.risk_analysis?.high_risk_percentage || 0}%`],
      ['AI Confidence', `${data.summary?.risk_analysis?.avg_ai_confidence || 0}%`],
      ['Authentic Documents', data.summary?.document_verification?.authentic_documents || 0],
      ['Fake Documents', data.summary?.document_verification?.fake_documents || 0],
      ['Avg Authenticity Score', data.summary?.document_verification?.avg_authenticity_score || 0]
    ];
    
    const overviewSheet = XLSX.utils.aoa_to_sheet(overviewData);
    XLSX.utils.book_append_sheet(workbook, overviewSheet, 'Overview');
    
    // Trends Sheet
    if (data.trends && data.trends.length > 0) {
      const trendsData = [
        ['Date', 'High Risk', 'Medium Risk', 'Low Risk', 'Total'],
        ...data.trends.map(trend => [
          trend.date,
          trend.high_risk,
          trend.medium_risk,
          trend.low_risk,
          trend.total
        ])
      ];
      
      const trendsSheet = XLSX.utils.aoa_to_sheet(trendsData);
      XLSX.utils.book_append_sheet(workbook, trendsSheet, 'Fraud Trends');
    }
    
    // Sectors Sheet
    if (data.sectors && data.sectors.length > 0) {
      const sectorsData = [
        ['Sector', 'Total Cases', 'High Risk Cases', 'High Risk %', 'Risk Level'],
        ...data.sectors.map(sector => [
          sector.sector,
          sector.total_cases,
          sector.high_risk_cases,
          sector.high_risk_percentage,
          sector.risk_level
        ])
      ];
      
      const sectorsSheet = XLSX.utils.aoa_to_sheet(sectorsData);
      XLSX.utils.book_append_sheet(workbook, sectorsSheet, 'Sector Analysis');
    }
    
    // Regions Sheet
    if (data.regions && data.regions.length > 0) {
      const regionsData = [
        ['Region', 'Total Cases', 'High Risk Cases', 'High Risk %', 'Category'],
        ...data.regions.map(region => [
          region.region,
          region.total_cases,
          region.high_risk_cases,
          region.high_risk_percentage,
          region.population_category
        ])
      ];
      
      const regionsSheet = XLSX.utils.aoa_to_sheet(regionsData);
      XLSX.utils.book_append_sheet(workbook, regionsSheet, 'Regional Analysis');
    }
    
    XLSX.writeFile(workbook, filename);
  }
  
  static exportToJSON(data: ExportData, filename: string = 'iris-analytics-data.json') {
    const exportData = {
      generated_at: new Date().toISOString(),
      platform_summary: data.summary,
      fraud_trends: data.trends,
      sector_analysis: data.sectors,
      regional_analysis: data.regions
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}
