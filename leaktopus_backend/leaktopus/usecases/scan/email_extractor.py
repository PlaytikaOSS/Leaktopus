import re


class EmailExtractor:
    def __init__(self, organization_domains):
        self.organization_domains = organization_domains

    def extract_organization_emails(self, content):
        org_emails = set()
        emails = self.extract_emails_from_content(content)
        for email in emails:
            if email.split("@")[1] in self.organization_domains:
                org_emails.add(email)

        return list(org_emails)

    def extract_emails_from_content(self, content):
        return re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", content)
