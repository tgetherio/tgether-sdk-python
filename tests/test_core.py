import pytest
import time
from tgether_sdk.core import TgetherSDK

TEST_PRIVATE_KEY = "0x59c6995e998f97a5a0044966f094538c1f62d44e9d3c7ec2ce9e5d5e7b8d2f48"  # test key
CONTRACT_ADDRESS = "0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC"
CHAIN_ID = 42161


@pytest.fixture
def sdk():
    return TgetherSDK(TEST_PRIVATE_KEY, CONTRACT_ADDRESS, CHAIN_ID)


def test_sign_order(sdk):
    vendor_id = 1
    vendor_order_id = "ORDER123"
    total_amount = 1_000_000

    result = sdk.sign_order(vendor_id, vendor_order_id, total_amount)

    assert "order" in result
    assert "signature" in result
    assert "signer" in result
    assert result["order"]["vendorOrderId"] == vendor_order_id
    assert result["order"]["totalAmount"] == total_amount
    assert result["signer"] == sdk.account.address


def test_verify_signature(sdk):
    vendor_id = 1
    vendor_order_id = "ORDER456"
    total_amount = 2_000_000

    signed = sdk.sign_order(vendor_id, vendor_order_id, total_amount)
    recovered = sdk.verify_signature(signed["order"], signed["signature"])

    assert recovered == sdk.account.address


def test_generate_order_response(sdk):
    vendor_id = 2
    vendor_order_id = "ORDER789"
    total_amount = 3_000_000

    response = sdk.generate_order_response(vendor_id, vendor_order_id, total_amount)

    assert response["code"] == "TGETHER_NEEDS_PAYMENT"
    assert response["order"]["vendorOrderId"] == vendor_order_id
    assert response["contract"] == CONTRACT_ADDRESS
    assert response["chainId"] == CHAIN_ID
    assert response["amount"] == total_amount
    assert "signature" in response
