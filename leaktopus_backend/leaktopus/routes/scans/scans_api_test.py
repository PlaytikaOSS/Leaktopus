from leaktopus_backend.leaktopus.routes.scans.scans_api import ScanUseCase, ScanRequest, ScanStatusService


def test_should_scan_succesfully():
    scan_status_service = ScanStatusService()
    request = ScanRequest(search_query="test")
    use_case = ScanUseCase(
        scan_status_service
    )
    response = use_case.execute(request)
    assert response.scan_id() is not None
