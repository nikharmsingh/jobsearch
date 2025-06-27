import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time
from config import Config

class CompanyDomainFinder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def find_domain(self, company_name):
        """Find company domain using multiple methods"""
        methods = [
            self._try_clearbit_api,
            self._try_apollo_api,
            self._try_google_search,
            self._try_direct_guess
        ]
        
        for method in methods:
            try:
                result = method(company_name)
                if result:
                    return result
            except Exception as e:
                print(f"Error in {method.__name__}: {e}")
                continue
        
        return None
    
    def _try_clearbit_api(self, company_name):
        """Try Clearbit API to find company domain"""
        api_key = Config.CLEARBIT_API_KEY
        if not api_key:
            return None
        
        url = f"https://company.clearbit.com/v1/domains/find"
        params = {'name': company_name}
        headers = {'Authorization': f'Bearer {api_key}'}
        
        response = self.session.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('domain')
        
        return None
    
    def _try_apollo_api(self, company_name):
        """Try Apollo.io API to find company domain"""
        api_key = Config.APOLLO_API_KEY
        if not api_key:
            return None

        url = "https://api.apollo.io/api/v1/organizations/search"
        headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'X-Api-Key': api_key
        }

        search_params = {
            "organization_names": [company_name],
            "per_page": 5
        }

        try:
            response = self.session.post(url, headers=headers, json=search_params)
            if response.status_code == 200:
                data = response.json()
                organizations = data.get('organizations', [])

                for org in organizations:
                    # Look for exact or close match
                    org_name = org.get('name', '').lower()
                    if company_name.lower() in org_name or org_name in company_name.lower():
                        domain = org.get('primary_domain')
                        if domain:
                            return domain

                        # Fallback to website_url domain extraction
                        website_url = org.get('website_url')
                        if website_url:
                            return self._extract_domain_from_url(website_url)

        except Exception as e:
            print(f"Apollo API error: {e}")

        return None
    
    def _try_google_search(self, company_name):
        """Try Google Custom Search API"""
        api_key = Config.GOOGLE_API_KEY
        cse_id = Config.GOOGLE_CSE_ID
        
        if not api_key or not cse_id:
            return self._try_google_scraping(company_name)
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': f'"{company_name}" official website',
            'num': 5
        }
        
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            for item in items:
                domain = self._extract_domain_from_url(item.get('link', ''))
                if domain and self._is_likely_company_domain(domain, company_name):
                    return domain
        
        return None
    
    def _try_google_scraping(self, company_name):
        """Fallback: scrape Google search results"""
        try:
            query = f'"{company_name}" official website'
            url = f"https://www.google.com/search?q={query}"
            
            response = self.session.get(url)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)
            
            for link in links[:10]:  # Check first 10 links
                href = link.get('href', '')
                if href.startswith('/url?q='):
                    # Extract actual URL from Google redirect
                    actual_url = href.split('/url?q=')[1].split('&')[0]
                    domain = self._extract_domain_from_url(actual_url)
                    if domain and self._is_likely_company_domain(domain, company_name):
                        return domain
            
            time.sleep(1)  # Be respectful to Google
            return None
            
        except Exception:
            return None
    
    def _try_direct_guess(self, company_name):
        """Try common domain patterns"""
        # Clean company name
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', company_name.lower())
        clean_name = re.sub(r'\s+', '', clean_name)
        
        # Common patterns
        patterns = [
            f"{clean_name}.com",
            f"{clean_name}.org",
            f"{clean_name}.net",
            f"{clean_name}inc.com",
            f"{clean_name}corp.com",
        ]
        
        # Try variations for multi-word companies
        words = company_name.lower().split()
        if len(words) > 1:
            patterns.extend([
                f"{''.join(words)}.com",
                f"{words[0]}.com",
                f"{words[0]}{words[-1]}.com"
            ])
        
        for pattern in patterns:
            if self._test_domain(pattern):
                return pattern
        
        return None
    
    def _extract_domain_from_url(self, url):
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return None
    
    def _is_likely_company_domain(self, domain, company_name):
        """Check if domain is likely the company's official domain"""
        if not domain:
            return False
        
        # Skip common non-company domains
        skip_domains = [
            'google.com', 'facebook.com', 'linkedin.com', 'twitter.com',
            'youtube.com', 'wikipedia.org', 'crunchbase.com', 'bloomberg.com'
        ]
        
        if any(skip in domain for skip in skip_domains):
            return False
        
        # Check if company name appears in domain
        clean_company = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
        clean_domain = re.sub(r'[^a-zA-Z0-9]', '', domain.split('.')[0])
        
        return clean_company in clean_domain or clean_domain in clean_company
    
    def _test_domain(self, domain):
        """Test if domain exists and responds"""
        try:
            response = self.session.head(f"http://{domain}", timeout=5)
            return response.status_code < 400
        except:
            try:
                response = self.session.head(f"https://{domain}", timeout=5)
                return response.status_code < 400
            except:
                return False
