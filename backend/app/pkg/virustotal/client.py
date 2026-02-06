import httpx
from typing import Optional, List
from dataclasses import dataclass
import ipaddress
from app.pkg.logger import logger

from app.core.config import get_settings


@dataclass
class VTResult:
    detected: bool
    positives: int
    total: int
    permalink: Optional[str] = None
    response: Optional[dict] = None

    def is_malicious(self, threshold: int = 3) -> bool:
        return self.positives >= threshold


class VirusTotalClient:
    BASE_URL = "https://www.virustotal.com/api/v3"

    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.VIRUSTOTAL_API_KEY
        self.headers = {"x-apikey": self.api_key} if self.api_key else {}

    def _is_external_ip(self, ip: str) -> bool:
        """Check if IP is external (not private/reserved)"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return not (
                ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_reserved
                or ip_obj.is_multicast
                or ip_obj.is_link_local
            )
        except ValueError:
            return False

    async def _get(
        self, endpoint: str, params: Optional[dict] = None
    ) -> Optional[dict]:
        """Send GET request to VirusTotal API"""
        url = f"{self.BASE_URL}{endpoint}"
        logger.debug(f"Querying VirusTotal: {endpoint}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, headers=self.headers, params=params, timeout=10.0
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None  # Not found is a valid result (clean)
                else:
                    logger.warning(
                        f"VirusTotal API error {response.status_code}: {response.text}"
                    )
                    return None
        except Exception as e:
            logger.error(f"VirusTotal request failed: {e}")
            return None

    async def check_ip(self, ip: str) -> VTResult:
        """Check IP against VirusTotal"""
        if not self.api_key or not self._is_external_ip(ip):
            return VTResult(detected=False, positives=0, total=0)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/ip_addresses/{ip}",
                    headers=self.headers,
                    timeout=30.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    stats = (
                        data.get("data", {})
                        .get("attributes", {})
                        .get("last_analysis_stats", {})
                    )
                    malicious = stats.get("malicious", 0)
                    suspicious = stats.get("suspicious", 0)
                    total = sum(stats.values()) if stats else 0
                    return VTResult(
                        detected=malicious > 0 or suspicious > 0,
                        positives=malicious + suspicious,
                        total=total,
                        permalink=f"https://www.virustotal.com/gui/ip-address/{ip}",
                        response=data,
                    )
        except Exception:
            pass
        return VTResult(detected=False, positives=0, total=0)

    async def check_domain(self, domain: str) -> VTResult:
        """Check domain against VirusTotal"""
        if not self.api_key:
            return VTResult(detected=False, positives=0, total=0)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/domains/{domain}",
                    headers=self.headers,
                    timeout=30.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    stats = (
                        data.get("data", {})
                        .get("attributes", {})
                        .get("last_analysis_stats", {})
                    )
                    malicious = stats.get("malicious", 0)
                    suspicious = stats.get("suspicious", 0)
                    total = sum(stats.values()) if stats else 0
                    return VTResult(
                        detected=malicious > 0 or suspicious > 0,
                        positives=malicious + suspicious,
                        total=total,
                        permalink=f"https://www.virustotal.com/gui/domain/{domain}",
                        response=data,
                    )
        except Exception:
            pass
        return VTResult(detected=False, positives=0, total=0)

    async def check_url(self, url: str) -> VTResult:
        """Check URL against VirusTotal"""
        if not self.api_key:
            return VTResult(detected=False, positives=0, total=0)

        try:
            import base64

            url_id = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/urls/{url_id}",
                    headers=self.headers,
                    timeout=30.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    stats = (
                        data.get("data", {})
                        .get("attributes", {})
                        .get("last_analysis_stats", {})
                    )
                    malicious = stats.get("malicious", 0)
                    suspicious = stats.get("suspicious", 0)
                    total = sum(stats.values()) if stats else 0
                    return VTResult(
                        detected=malicious > 0 or suspicious > 0,
                        positives=malicious + suspicious,
                        total=total,
                        permalink=f"https://www.virustotal.com/gui/url/{url_id}",
                        response=data,
                    )
        except Exception:
            pass
        return VTResult(detected=False, positives=0, total=0)

    async def check_hash(self, file_hash: str) -> VTResult:
        """Check file hash against VirusTotal"""
        if not self.api_key:
            return VTResult(detected=False, positives=0, total=0)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/files/{file_hash}",
                    headers=self.headers,
                    timeout=30.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    stats = (
                        data.get("data", {})
                        .get("attributes", {})
                        .get("last_analysis_stats", {})
                    )
                    malicious = stats.get("malicious", 0)
                    suspicious = stats.get("suspicious", 0)
                    total = sum(stats.values()) if stats else 0
                    return VTResult(
                        detected=malicious > 0 or suspicious > 0,
                        positives=malicious + suspicious,
                        total=total,
                        permalink=f"https://www.virustotal.com/gui/file/{file_hash}",
                        response=data,
                    )
        except Exception:
            pass
        return VTResult(detected=False, positives=0, total=0)
