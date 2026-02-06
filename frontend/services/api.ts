import { SecurityAlert } from '../types';

const API_BASE_URL = '/api/v1';

export interface AlertListResponse {
    items: SecurityAlert[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

export interface AlertStats {
    total_critical: number;
    by_level: {
        name: string;
        count: number;
        color: string;
    }[];
}

export const fetchAlerts = async (
    page = 1,
    pageSize = 20,
    sortBy = 'upload_time',
    sortOrder = 'desc',
    filters?: {
        level?: string;
        verdict?: string;
        attackerIp?: string;
    }
): Promise<AlertListResponse> => {
    const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        sort_by: sortBy,
        sort_order: sortOrder,
    });

    if (filters) {
        if (filters.level && filters.level !== 'All Levels') {
            params.append('alert_level', filters.level);
        }
        if (filters.verdict && filters.verdict !== 'All Verdicts') {
            params.append('verdict', filters.verdict);
        }
        if (filters.attackerIp) {
            params.append('source_ip', filters.attackerIp);
        }
    }

    const response = await fetch(`${API_BASE_URL}/alerts?${params}`);

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch alerts: ${response.status} ${errorText}`);
    }

    return response.json();
};

export const fetchAlertStats = async (): Promise<AlertStats> => {
    const response = await fetch(`${API_BASE_URL}/alerts/stats/dashboard`);

    if (!response.ok) {
        throw new Error(`Failed to fetch stats: ${response.status}`);
    }

    return response.json();
};

export const analyzeAlert = async (alertJson: string): Promise<string> => {
    try {
        let parsedJson;
        try {
            parsedJson = JSON.parse(alertJson);
        } catch (e) {
            return "**Error**: Invalid JSON format.";
        }

        const response = await fetch(`${API_BASE_URL}/analysis/alert`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                alert_payload: parsedJson
            }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Backend analysis failed: ${response.status} ${errorText}`);
        }

        const data = await response.json();

        // Format the structured backend response into Markdown for TriageStation
        return formatBackendResponseToMarkdown(data);

    } catch (error) {
        console.error("Analysis Failed:", error);
        return `**Error running analysis**: ${(error as Error).message}.`;
    }
};

const formatBackendResponseToMarkdown = (data: any): string => {
    // Extract sections from backend response (schema TriageAnalysisResponse / dict)
    const classification = data.classification;
    const analysis = data.analysis;
    const attackMapping = data.attack_mapping;
    const entities = data.entities;
    const ti = data.ti_matching;

    let md = "";

    // 1. Executive Summary (from Analysis Conclusion)
    md += "### Executive Summary\n";
    if (analysis?.conclusion) {
        md += `${analysis.conclusion}\n\n`;
    } else {
        md += "No conclusion generated.\n\n";
    }

    // 2. Risk Assessment
    md += "### Risk Assessment\n";
    if (classification) {
        md += `**Category**: ${classification.category}\n`;
        md += `**Source Type**: ${classification.source_type}\n`;
        md += `**Reasoning**: ${classification.reasoning}\n\n`;
    }
    if (ti && ti.malicious_found > 0) {
        md += `**Threat Intel**: Found ${ti.malicious_found} malicious indicators out of ${ti.total_checked} checked.\n\n`;
    }

    // 3. MITRE ATT&CK
    if (attackMapping) {
        md += "### MITRE ATT&CK Mapping\n";
        md += `**Tactic**: ${attackMapping.tactic}\n`;
        md += `**Technique**: ${attackMapping.technique}\n`;
        md += `**Details**: ${attackMapping.reasoning}\n\n`;
    }

    // 4. Extracted Entities (Optional but helpful)
    if (entities) {
        const ips = entities.ips?.length || 0;
        const domains = entities.domains?.length || 0;
        if (ips > 0 || domains > 0) {
            md += "### Key Indicators\n";
            if (ips > 0) md += `- IPs: ${entities.ips.join(', ')}\n`;
            if (domains > 0) md += `- Domains: ${entities.domains.join(', ')}\n`;
            md += "\n";
        }
    }

    // 5. Recommended Actions (from Analysis Steps)
    md += "### Recommended Actions\n";
    if (analysis?.investigation_steps && Array.isArray(analysis.investigation_steps)) {
        analysis.investigation_steps.forEach((step: any) => {
            md += `- **${step.title}**: ${step.details}\n`;
        });
    } else {
        md += "- Review alert context and correlated logs.\n";
        md += "- Isolate affected host if malicious activity is confirmed.\n";
    }

    return md;
};

