import requests
import re
import time
from config import Config

class SerpHRFinder:
    """
    SERP API service for finding HR professionals based in India
    Uses SerpApi to search Google, LinkedIn, and other platforms for real HR contacts
    """
    
    def __init__(self):
        self.api_key = Config.SERP_API_KEY
        self.base_url = "https://serpapi.com/search"
        
    def find_hr_professionals(self, company_name, company_domain=None):
        """
        Find HR professionals for a company using SERP API
        Focuses on India-based HR professionals
        """
        print(f"\n🔍 SERP API: Searching for HR professionals at {company_name} in India...")
        
        if not self.api_key:
            print("❌ SERP API key not configured")
            return []
        
        results = []
        
        # Multiple search strategies
        search_strategies = [
            self._search_linkedin_hr_profiles,
            self._search_company_hr_pages,
            self._search_job_postings_contacts,
            self._search_professional_networks
        ]
        
        for strategy in search_strategies:
            try:
                strategy_results = strategy(company_name, company_domain)
                if strategy_results:
                    results.extend(strategy_results)
                    print(f"  ✅ Found {len(strategy_results)} contacts via {strategy.__name__}")
                else:
                    print(f"  ❌ No results from {strategy.__name__}")
                    
                # Rate limiting - be respectful to SERP API
                time.sleep(1)
                
            except Exception as e:
                print(f"  ⚠️ Error in {strategy.__name__}: {e}")
                continue
        
        # Remove duplicates and sort by confidence
        unique_results = self._deduplicate_results(results)
        
        # Sort by confidence and India preference
        unique_results.sort(key=lambda x: (
            -x.get('confidence', 0),
            x.get('location') == 'India',
            'LinkedIn' in x.get('source', '')
        ), reverse=True)
        
        final_results = unique_results[:10]  # Top 10 results
        
        print(f"\n✅ SERP API found {len(final_results)} unique HR contacts:")
        for i, contact in enumerate(final_results, 1):
            location = f" ({contact.get('location', 'Unknown')})" if contact.get('location') else ""
            print(f"  {i}. {contact['name']} - {contact['email']}{location}")
            print(f"     Position: {contact.get('position', 'N/A')} | Source: {contact.get('source', 'N/A')}")
        
        return final_results
    
    def _search_linkedin_hr_profiles(self, company_name, company_domain):
        """Search LinkedIn for HR professionals at the company"""
        results = []
        
        # LinkedIn-specific search queries for India-based HR professionals
        linkedin_queries = [
            f'"{company_name}" HR Manager India site:linkedin.com',
            f'"{company_name}" Human Resources India site:linkedin.com',
            f'"{company_name}" Talent Acquisition India site:linkedin.com',
            f'"{company_name}" Recruiter India site:linkedin.com',
            f'"HR Manager at {company_name}" India site:linkedin.com',
            f'"Talent Acquisition at {company_name}" India site:linkedin.com'
        ]
        
        for query in linkedin_queries[:3]:  # Limit to avoid quota exhaustion
            try:
                print(f"    🔍 LinkedIn search: {query}")
                search_results = self._perform_serp_search(query, search_type='google')
                
                for result in search_results:
                    if 'linkedin.com/in/' in result.get('link', ''):
                        person_info = self._extract_linkedin_person_info(result, company_name)
                        if person_info and self._is_india_based(result.get('snippet', '')):
                            # Generate email candidates for this real person
                            if company_domain:
                                email_candidates = self._generate_person_email_candidates(
                                    person_info['name'], company_domain
                                )
                                if email_candidates:
                                    results.append({
                                        'name': person_info['name'],
                                        'email': email_candidates[0],  # Most likely email
                                        'position': person_info['position'],
                                        'source': 'SERP API - LinkedIn Profile',
                                        'confidence': 85,
                                        'location': 'India',
                                        'linkedin_url': result.get('link'),
                                        'alternative_emails': email_candidates[1:3]
                                    })
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"    ❌ LinkedIn search error: {e}")
                continue
        
        return results
    
    def _search_company_hr_pages(self, company_name, company_domain):
        """Search for company HR pages and team directories"""
        results = []
        
        if not company_domain:
            return results
        
        # Company-specific searches
        company_queries = [
            f'site:{company_domain} "HR team" OR "Human Resources" contact India',
            f'site:{company_domain} "careers" OR "jobs" contact email India',
            f'site:{company_domain} "about us" HR team India',
            f'"{company_name}" HR contact email India'
        ]
        
        for query in company_queries[:2]:  # Limit searches
            try:
                print(f"    🔍 Company search: {query}")
                search_results = self._perform_serp_search(query, search_type='google')
                
                for result in search_results:
                    # Extract HR contacts from company pages
                    hr_contacts = self._extract_hr_contacts_from_result(result, company_domain)
                    for contact in hr_contacts:
                        if self._is_india_based(result.get('snippet', '')):
                            contact['source'] = 'SERP API - Company Website'
                            contact['confidence'] = 80
                            contact['location'] = 'India'
                            results.append(contact)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"    ❌ Company search error: {e}")
                continue
        
        return results
    
    def _search_job_postings_contacts(self, company_name, company_domain):
        """Search job postings for HR contact information"""
        results = []
        
        # Job board searches
        job_queries = [
            f'"{company_name}" HR contact apply India site:naukri.com',
            f'"{company_name}" recruiter contact India site:linkedin.com/jobs',
            f'"{company_name}" hiring manager email India',
            f'"{company_name}" talent acquisition contact India'
        ]
        
        for query in job_queries[:2]:  # Limit searches
            try:
                print(f"    🔍 Job posting search: {query}")
                search_results = self._perform_serp_search(query, search_type='google')
                
                for result in search_results:
                    # Look for HR contacts in job postings
                    job_contacts = self._extract_job_posting_contacts(result, company_name, company_domain)
                    for contact in job_contacts:
                        if self._is_india_based(result.get('snippet', '')):
                            contact['source'] = 'SERP API - Job Posting'
                            contact['confidence'] = 75
                            contact['location'] = 'India'
                            results.append(contact)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"    ❌ Job posting search error: {e}")
                continue
        
        return results
    
    def _search_professional_networks(self, company_name, company_domain):
        """Search professional networks and directories"""
        results = []
        
        # Professional network searches
        network_queries = [
            f'"{company_name}" HR India site:rocketreach.co',
            f'"{company_name}" Human Resources India contact',
            f'"{company_name}" talent team India email'
        ]
        
        for query in network_queries[:2]:  # Limit searches
            try:
                print(f"    🔍 Professional network search: {query}")
                search_results = self._perform_serp_search(query, search_type='google')
                
                for result in search_results:
                    # Extract contacts from professional networks
                    network_contacts = self._extract_network_contacts(result, company_domain)
                    for contact in network_contacts:
                        if self._is_india_based(result.get('snippet', '')):
                            contact['source'] = 'SERP API - Professional Network'
                            contact['confidence'] = 70
                            contact['location'] = 'India'
                            results.append(contact)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"    ❌ Professional network search error: {e}")
                continue
        
        return results
    
    def _perform_serp_search(self, query, search_type='google', num_results=10):
        """Perform search using SERP API"""
        try:
            params = {
                'api_key': self.api_key,
                'engine': search_type,
                'q': query,
                'num': num_results,
                'gl': 'in',  # India geolocation
                'hl': 'en'   # English language
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('organic_results', [])
            else:
                print(f"SERP API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"SERP API request error: {e}")
            return []
    
    def _extract_linkedin_person_info(self, result, company_name):
        """Extract person information from LinkedIn search result"""
        try:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            
            # Extract name and position from LinkedIn title
            # Pattern: "Name - Position at Company | LinkedIn"
            name_match = re.search(r'^([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*[-–]\s*(.+?)\s*(?:\||at\s)', title)
            
            if name_match:
                name = name_match.group(1).strip()
                position_and_company = name_match.group(2).strip()
                
                # Validate company association
                full_text = f"{title} {snippet}".lower()
                if company_name.lower() in full_text:
                    # Extract position
                    if ' at ' in position_and_company:
                        position = position_and_company.split(' at ')[0].strip()
                    else:
                        position = position_and_company
                    
                    # Validate HR-related position
                    if self._is_hr_related_title(position):
                        return {
                            'name': name,
                            'position': position
                        }
            
            return None
            
        except Exception as e:
            print(f"Error extracting LinkedIn info: {e}")
            return None

    def _extract_hr_contacts_from_result(self, result, company_domain):
        """Extract HR contacts from search result"""
        contacts = []

        try:
            snippet = result.get('snippet', '')
            title = result.get('title', '')
            full_text = f"{title} {snippet}"

            # Look for email addresses
            emails = self._extract_emails_from_text(full_text)

            for email in emails:
                if company_domain and company_domain in email:
                    # Try to find associated name and title
                    person_info = self._extract_person_info_from_context(full_text, email)

                    if person_info and self._is_hr_related_title(person_info.get('position', '')):
                        contacts.append({
                            'name': person_info['name'],
                            'email': email,
                            'position': person_info['position']
                        })

            return contacts

        except Exception as e:
            print(f"Error extracting HR contacts: {e}")
            return []

    def _extract_job_posting_contacts(self, result, company_name, company_domain):
        """Extract HR contacts from job posting results"""
        contacts = []

        try:
            snippet = result.get('snippet', '')
            title = result.get('title', '')
            full_text = f"{title} {snippet}"

            # Validate this is actually for the target company
            if company_name.lower() not in full_text.lower():
                return []

            # Look for HR-related contacts in job postings
            emails = self._extract_emails_from_text(full_text)

            for email in emails:
                if company_domain and company_domain in email:
                    # Look for HR context
                    if any(keyword in full_text.lower() for keyword in ['hr', 'human resources', 'recruiter', 'talent']):
                        person_info = self._extract_person_info_from_context(full_text, email)

                        if person_info:
                            contacts.append({
                                'name': person_info['name'],
                                'email': email,
                                'position': person_info.get('position', 'HR Professional')
                            })

            return contacts

        except Exception as e:
            print(f"Error extracting job posting contacts: {e}")
            return []

    def _extract_network_contacts(self, result, company_domain):
        """Extract contacts from professional networks"""
        contacts = []

        try:
            snippet = result.get('snippet', '')
            title = result.get('title', '')
            full_text = f"{title} {snippet}"

            # Look for email addresses
            emails = self._extract_emails_from_text(full_text)

            for email in emails:
                if company_domain and company_domain in email:
                    person_info = self._extract_person_info_from_context(full_text, email)

                    if person_info:
                        contacts.append({
                            'name': person_info['name'],
                            'email': email,
                            'position': person_info.get('position', 'HR Professional')
                        })

            return contacts

        except Exception as e:
            print(f"Error extracting network contacts: {e}")
            return []

    def _extract_emails_from_text(self, text):
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)

    def _extract_person_info_from_context(self, text, email):
        """Extract person's name and position from context around email"""
        try:
            # Look for name patterns near the email
            name_patterns = [
                r'([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*[-–]\s*([^|]+)',  # "John Doe - HR Manager"
                r'([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*,\s*([^,]+)',      # "John Doe, HR Manager"
                r'([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*\|\s*([^|]+)',     # "John Doe | HR Manager"
            ]

            for pattern in name_patterns:
                match = re.search(pattern, text)
                if match:
                    name = match.group(1).strip()
                    position = match.group(2).strip()

                    if self._is_valid_person_name(name):
                        return {
                            'name': name,
                            'position': position if self._is_hr_related_title(position) else 'HR Professional'
                        }

            # If no name found, try to extract from email
            email_prefix = email.split('@')[0]
            if '.' in email_prefix:
                parts = email_prefix.split('.')
                if len(parts) == 2 and all(part.isalpha() for part in parts):
                    name = f"{parts[0].title()} {parts[1].title()}"
                    return {
                        'name': name,
                        'position': 'HR Professional'
                    }

            return None

        except Exception as e:
            print(f"Error extracting person info: {e}")
            return None

    def _generate_person_email_candidates(self, name, domain):
        """Generate likely email addresses for a person"""
        if not name or not domain:
            return []

        name_parts = name.lower().replace('.', '').replace(',', '').split()
        if len(name_parts) < 2:
            return []

        first_name = name_parts[0]
        last_name = name_parts[-1]

        # Generate email patterns in order of likelihood
        email_patterns = [
            f"{first_name}.{last_name}@{domain}",
            f"{first_name}{last_name}@{domain}",
            f"{first_name}@{domain}",
            f"{first_name[0]}{last_name}@{domain}",
            f"{first_name}_{last_name}@{domain}",
            f"{last_name}.{first_name}@{domain}"
        ]

        return email_patterns

    def _is_india_based(self, text):
        """Check if the text indicates India-based location"""
        india_indicators = [
            'india', 'mumbai', 'delhi', 'bangalore', 'bengaluru', 'hyderabad',
            'chennai', 'pune', 'kolkata', 'ahmedabad', 'gurgaon', 'gurugram',
            'noida', 'kochi', 'chandigarh', 'jaipur', 'indore', 'bhopal'
        ]

        text_lower = text.lower()
        return any(indicator in text_lower for indicator in india_indicators)

    def _is_hr_related_title(self, title):
        """Check if a job title is HR-related"""
        if not title:
            return False

        hr_keywords = [
            'hr', 'human resources', 'recruiting', 'recruiter', 'talent',
            'people', 'personnel', 'hiring', 'staffing', 'people operations'
        ]

        title_lower = title.lower()
        return any(keyword in title_lower for keyword in hr_keywords)

    def _is_valid_person_name(self, name):
        """Check if a string looks like a valid person name"""
        if not name:
            return False

        parts = name.split()
        if len(parts) < 2 or len(parts) > 3:
            return False

        # Each part should start with capital letter and be alphabetic
        for part in parts:
            if not part[0].isupper() or not part.isalpha():
                return False

        return True

    def _deduplicate_results(self, results):
        """Remove duplicate results based on email and name"""
        unique_results = []
        seen_emails = set()
        seen_names = set()

        for result in results:
            email = result['email']
            name = result.get('name', '').lower()

            if email not in seen_emails and name not in seen_names:
                unique_results.append(result)
                seen_emails.add(email)
                if name:
                    seen_names.add(name)

        return unique_results
