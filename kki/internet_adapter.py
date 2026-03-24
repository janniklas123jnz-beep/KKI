"""Leitstern Internet-Adapter — DuckDuckGo + Wikipedia Zugang für den Schwarm.

Nutzung:
    from kki.internet_adapter import LeitsternInternetAdapter
    adapter = LeitsternInternetAdapter()
    result = adapter.research("Quantenmechanik")
    print(result["top_article"]["extract"])
"""
from __future__ import annotations

import json
import urllib.request
import urllib.parse
import urllib.error
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SearchResult:
    """Ein einzelnes Suchergebnis."""
    title: str
    url: str
    snippet: str
    source: str  # "duckduckgo" | "wikipedia"


@dataclass
class WikipediaArtikel:
    """Eine Wikipedia-Artikel-Zusammenfassung."""
    title: str
    beschreibung: str
    url: str
    extrakt: str
    sprache: str = "de"


@dataclass
class RechercheErgebnis:
    """Kombiniertes Recherche-Ergebnis für einen Agenten."""
    anfrage: str
    wikipedia_treffer: List[SearchResult] = field(default_factory=list)
    duckduckgo_treffer: List[SearchResult] = field(default_factory=list)
    top_artikel: Optional[WikipediaArtikel] = None
    erfolgreich: bool = True
    fehler: Optional[str] = None

    def zusammenfassung(self) -> str:
        """Gibt eine lesbare Zusammenfassung des Recherche-Ergebnisses zurück."""
        lines = [f"🔍 Anfrage: {self.anfrage}"]
        if self.top_artikel:
            lines.append(f"\n📖 Wikipedia: {self.top_artikel.title}")
            lines.append(f"   {self.top_artikel.extrakt[:500]}...")
            lines.append(f"   URL: {self.top_artikel.url}")
        if self.wikipedia_treffer:
            lines.append(f"\n📚 Wikipedia-Suche ({len(self.wikipedia_treffer)} Treffer):")
            for r in self.wikipedia_treffer[:3]:
                lines.append(f"   • {r.title}: {r.url}")
        if self.duckduckgo_treffer:
            lines.append(f"\n🦆 DuckDuckGo ({len(self.duckduckgo_treffer)} Treffer):")
            for r in self.duckduckgo_treffer[:3]:
                lines.append(f"   • {r.title}")
        if not self.erfolgreich:
            lines.append(f"\n⚠️  Fehler: {self.fehler}")
        return "\n".join(lines)


class LeitsternInternetAdapter:
    """Internet-Zugang für Leitstern und seine Agenten.

    Kombiniert DuckDuckGo Instant Answers und Wikipedia REST API
    ohne externe Abhängigkeiten (nur Python stdlib urllib).

    Beispiel:
        adapter = LeitsternInternetAdapter()
        ergebnis = adapter.recherchiere("Photosyntheese")
        print(ergebnis.zusammenfassung())
    """

    DDG_API = "https://api.duckduckgo.com/"
    WIKI_API_TEMPLATE = "https://{lang}.wikipedia.org/w/api.php"
    WIKI_REST_TEMPLATE = "https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"

    def __init__(
        self,
        timeout: int = 15,
        user_agent: str = "Leitstern-KKI/1.0 (Schwarm-Forschungsagent)",
        standard_sprache: str = "de",
    ) -> None:
        self.timeout = timeout
        self.headers = {"User-Agent": user_agent}
        self.standard_sprache = standard_sprache

    def _get(self, url: str) -> bytes:
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return resp.read()

    def _get_json(self, url: str) -> dict | list:
        return json.loads(self._get(url).decode("utf-8"))

    # ── DuckDuckGo ────────────────────────────────────────────────────────────

    def suche_duckduckgo(self, anfrage: str, max_treffer: int = 5) -> List[SearchResult]:
        """Suche mit DuckDuckGo Instant Answer API (kostenlos, kein Key)."""
        params = urllib.parse.urlencode({
            "q": anfrage,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1",
        })
        try:
            data = self._get_json(f"{self.DDG_API}?{params}")
        except Exception as exc:
            return []

        results: List[SearchResult] = []

        if isinstance(data, dict) and data.get("AbstractText"):
            results.append(SearchResult(
                title=data.get("Heading", anfrage),
                url=data.get("AbstractURL", ""),
                snippet=data["AbstractText"],
                source="duckduckgo",
            ))

        for item in data.get("RelatedTopics", [])[:max_treffer]:
            if isinstance(item, dict) and "Text" in item and "FirstURL" in item:
                results.append(SearchResult(
                    title=item["Text"][:120],
                    url=item["FirstURL"],
                    snippet=item["Text"],
                    source="duckduckgo",
                ))
            if len(results) >= max_treffer:
                break

        return results[:max_treffer]

    # ── Wikipedia ─────────────────────────────────────────────────────────────

    def suche_wikipedia(
        self, anfrage: str, sprache: str = "", max_treffer: int = 5
    ) -> List[SearchResult]:
        """Suche Wikipedia-Artikel-Titel."""
        lang = sprache or self.standard_sprache
        base = self.WIKI_API_TEMPLATE.format(lang=lang)
        params = urllib.parse.urlencode({
            "action": "opensearch",
            "search": anfrage,
            "limit": max_treffer,
            "format": "json",
            "redirects": "resolve",
        })
        try:
            data = self._get_json(f"{base}?{params}")
        except Exception:
            return []

        if not isinstance(data, list) or len(data) < 4:
            return []

        _, titles, snippets, urls = data  # data[0] is the echo of the query string
        return [
            SearchResult(title=t, url=u, snippet=s or t, source="wikipedia")
            for t, s, u in zip(titles, snippets, urls)
        ]

    def hole_wikipedia_artikel(
        self, titel: str, sprache: str = ""
    ) -> Optional[WikipediaArtikel]:
        """Lade Zusammenfassung eines Wikipedia-Artikels."""
        lang = sprache or self.standard_sprache
        encoded = urllib.parse.quote(titel.replace(" ", "_"), safe="")
        url = self.WIKI_REST_TEMPLATE.format(lang=lang, title=encoded)
        try:
            data = self._get_json(url)
        except Exception:
            return None

        if not isinstance(data, dict):
            return None

        return WikipediaArtikel(
            title=data.get("title", titel),
            beschreibung=data.get("description", ""),
            url=(data.get("content_urls") or {}).get("desktop", {}).get("page", url),
            extrakt=data.get("extract", ""),
            sprache=lang,
        )

    # ── Kombinierte Recherche ─────────────────────────────────────────────────

    def recherchiere(
        self, anfrage: str, sprache: str = "", max_treffer: int = 5
    ) -> RechercheErgebnis:
        """Autonome Recherche: kombiniert Wikipedia + DuckDuckGo.

        Args:
            anfrage: Suchanfrage / Thema
            sprache: Sprachcode z.B. "de", "en" (Standard: self.standard_sprache)
            max_treffer: Maximale Ergebnisse pro Quelle

        Returns:
            RechercheErgebnis mit allen gefundenen Informationen
        """
        lang = sprache or self.standard_sprache
        ergebnis = RechercheErgebnis(anfrage=anfrage)

        try:
            ergebnis.wikipedia_treffer = self.suche_wikipedia(
                anfrage, sprache=lang, max_treffer=max_treffer
            )
            ergebnis.duckduckgo_treffer = self.suche_duckduckgo(
                anfrage, max_treffer=max_treffer
            )
            if ergebnis.wikipedia_treffer:
                ergebnis.top_artikel = self.hole_wikipedia_artikel(
                    ergebnis.wikipedia_treffer[0].title, sprache=lang
                )
        except Exception as exc:
            ergebnis.erfolgreich = False
            ergebnis.fehler = str(exc)

        return ergebnis

    def validiere_information(self, behauptung: str, kontext: str = "") -> dict:
        """Validiere eine Behauptung durch Gegenrecherche.

        Args:
            behauptung: Die zu prüfende Aussage
            kontext: Optionaler thematischer Kontext

        Returns:
            dict mit Validierungsergebnis und Quellen
        """
        anfrage = f"{behauptung} {kontext}".strip()
        ergebnis = self.recherchiere(anfrage)
        quellen = [r.url for r in ergebnis.wikipedia_treffer + ergebnis.duckduckgo_treffer if r.url]
        return {
            "behauptung": behauptung,
            "quellen_gefunden": len(quellen),
            "quellen": quellen[:5],
            "top_extrakt": ergebnis.top_artikel.extrakt if ergebnis.top_artikel else "",
            "validiert": ergebnis.erfolgreich and len(quellen) > 0,
        }

    def entdecke_themen(self, basis_thema: str, sprache: str = "") -> List[str]:
        """Entdecke verwandte Themen für autonome Wissenserweiterung.

        Args:
            basis_thema: Ausgangsthema
            sprache: Sprachcode

        Returns:
            Liste verwandter Themen
        """
        lang = sprache or self.standard_sprache
        results = self.suche_wikipedia(basis_thema, sprache=lang, max_treffer=8)
        ddg = self.suche_duckduckgo(basis_thema, max_treffer=5)
        themen = list({r.title for r in results + ddg if r.title and len(r.title) > 3})
        return themen[:10]
