import whois
from app.domain.ports import WhoisProvider


class GlobalWhoisService(WhoisProvider):
    def get_registrant(self, domain: str) -> str:
        try:
            w = whois.whois(domain)
            # Different registrars return different structures.
            # Usually 'org' or 'registrar' or 'name' gives a hint.
            # If available, we return the registrant organization or name.

            if w.org:
                return str(w.org)
            if w.name:
                return str(w.name)
            if w.registrar:
                return str(w.registrar)

            return "Unknown"
        except Exception:
            return "Hidden/Error"
