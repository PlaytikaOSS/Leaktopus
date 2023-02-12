from subprocess import check_output, CalledProcessError, STDOUT
from leaktopus.services.enhancement_module.enhancement_module_provider import EnhancementModuleProviderInterface
from leaktopus.services.enhancement_module.enhancement_module_service import EnhancementModuleException
from leaktopus.utils.common_imports import logger
from leaktopus.common.db_handler import add_domain, get_domain

class EnhancementModuleDomainsProvider(EnhancementModuleProviderInterface):
    def __init__(self, override_methods={}, **kwargs):
        self.override_methods = override_methods

    def get_provider_name(self):
        return "domains"

    def parse_domains_results(self, leak_service, url, output):
        domains = []

        for row in output.splitlines():
            row_parts = row.split(":")
            commit_sha = row_parts[0][2:]
            domains.append({
                "commit_sha": commit_sha,
                "domain": ':'.join(row_parts[1:]),
                "html_url": url[:-4] + "/commit/" + commit_sha
            })

        # Filter by unique domains.
        domains_unique = list({v['domain']: v for v in domains}.values())

        # Get leak from DB.
        leaks = leak_service.get_leaks(url=url)

        if not leaks:
            return False

        for domain in domains_unique:
            # Add the secret to the DB if not already exists
            if not get_domain(domain=domain["domain"]):
                add_domain(leaks[0].leak_id, domain["html_url"], domain["domain"])

    def guard_empty_organization_domains(self, potential_leak_source_request):
        if len(potential_leak_source_request.organization_domains) == 0:
            logger.info("No organization domains provided for enhancement module service")
            raise EnhancementModuleException("No organization domains provided for enhancement module service")

    def execute(self, potential_leak_source_request, leak_service, url, full_diff_dir):
        logger.info("Enhancement module domains is enhancing PLS {} stored in {}", url, full_diff_dir)

        try:
            self.guard_empty_organization_domains(potential_leak_source_request)

            # @todo Consider to match also IP addresses.
            domains_matching = "([a-zA-Z])+?://([a-zA-Z0-9\.\-_])*(" + "|".join(potential_leak_source_request.organization_domains) + ")"
            output = check_output([
                'egrep',
                '-Iiro',
                domains_matching,
                "."
            ], stderr=STDOUT, cwd=full_diff_dir).decode()

            if output:
                self.parse_domains_results(leak_service, url, output)
        except EnhancementModuleException:
            return False
        except CalledProcessError:
            return False