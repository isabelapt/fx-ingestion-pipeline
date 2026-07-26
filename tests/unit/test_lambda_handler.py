from datetime import date
from unittest.mock import MagicMock, patch
from src.adapters.lambda_handler import lambda_handler
from src.domain.entities import FXRateEntity, IngestionResult

@patch("src.adapters.lambda_handler.IngestFXRatesUseCase")
@patch("src.adapters.lambda_handler.S3Repository")
@patch("src.adapters.lambda_handler.FXApiClient")
def test_lambda_handler_success(mock_api, mock_s3, mock_use_case_cls):
    # Setup da entidade mockada do domínio
    mock_entity = FXRateEntity(
        base_currency="USD",
        observation_date=date(2026, 7, 26),
        rates={"BRL": 5.40}
    )
    
    mock_result = IngestionResult(
        entity=mock_entity,
        s3_path="raw/year=2026/month=07/day=26/USD_20260726.json",
        is_anomaly=False,
        quarantined=False
    )

    mock_use_case_inst = MagicMock()
    mock_use_case_inst.execute.return_value = mock_result
    mock_use_case_cls.return_value = mock_use_case_inst

    # Execução
    event = {"base_currency": "USD", "date": "2026-07-26"}
    response = lambda_handler(event, None)

    # Assertivas
    assert response["statusCode"] == 200
    assert response["body"]["identity"] == "USD_20260726"
    assert response["body"]["s3_path"] == "raw/year=2026/month=07/day=26/USD_20260726.json"
    assert response["body"]["is_anomaly"] is False
    mock_use_case_inst.execute.assert_called_once_with(base_currency="USD", observation_date="2026-07-26")