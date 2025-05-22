# tgether_sdk/core.py

from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_utils import keccak
import time
from typing import Optional, Dict, Any

class TgetherSDK:
    def __init__(self, private_key: str, verifying_contract: str, chain_id: int = 42161):
        self.account = Account.from_key(private_key)
        self.chain_id = chain_id
        self.verifying_contract = verifying_contract

        self.domain = {
            "name": "TgetherPOS",
            "version": "1",
            "chainId": chain_id,
            "verifyingContract": verifying_contract,
        }

        self.types = {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "OrderAuth": [
                {"name": "vendorId", "type": "uint256"},
                {"name": "vendorOrderId", "type": "string"},
                {"name": "totalAmount", "type": "uint256"},
                {"name": "validUntil", "type": "uint256"},
                {"name": "nonce", "type": "string"},
            ]
        }

    def sign_order(
        self,
        vendor_id: int,
        vendor_order_id: str,
        total_amount: int,
        valid_until: Optional[int] = None,
        nonce: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sign a vendor-authorized order using EIP-712 structured data.

        Args:
            vendor_id: The vendor's ID (uint256)
            vendor_order_id: A unique order reference string
            total_amount: Order total in USDC (integer, 6 decimals)
            valid_until: Expiry timestamp (defaults to 1 hour from now)
            nonce: Unique per-order nonce (defaults to vendorOrderId + ":nonce")

        Returns:
            A dictionary with the signed order, signature, and signer address.
        """
        if not valid_until:
            valid_until = int(time.time()) + 3600  # default 1 hour expiry
        if not nonce:
            nonce = vendor_order_id + ":nonce"

        order = {
            "vendorId": vendor_id,
            "vendorOrderId": vendor_order_id,
            "totalAmount": total_amount,
            "validUntil": valid_until,
            "nonce": nonce
        }

        message = {
            "types": self.types,
            "domain": self.domain,
            "primaryType": "OrderAuth",
            "message": order
        }

        encoded = encode_typed_data(
            domain_data=self.domain,
            message_types={"OrderAuth": self.types["OrderAuth"]},
            message_data=order
        )
        signed = self.account.sign_message(encoded)

        return {
            "order": order,
            "signature": signed.signature.hex(),
            "signer": self.account.address
        }

    def verify_signature(self, order: Dict[str, Any], signature: str) -> str:
        """
        Recover the signer address from a signed order.

        Args:
            order: The order dictionary that was signed
            signature: The hex-encoded signature

        Returns:
            The recovered Ethereum address of the signer
        """
        message = {
            "types": self.types,
            "domain": self.domain,
            "primaryType": "OrderAuth",
            "message": order
        }
        encoded = encode_typed_data(
            domain_data=self.domain,
            message_types={"OrderAuth": self.types["OrderAuth"]},
            message_data=order
        )
        return Account.recover_message(encoded, signature=signature)

    def generate_order_response(
        self,
        vendor_id: int,
        vendor_order_id: str,
        total_amount: int,
        pay_url: Optional[str] = None,
        valid_until: Optional[int] = None,
        nonce: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a signed order response payload for client-side consumption.

        Args:
            vendor_id: The vendor's ID
            vendor_order_id: A unique vendor order ID
            total_amount: The total amount the user needs to pay
            pay_url: Optional URL to direct user to payment UI
            valid_until: Optional expiry timestamp
            nonce: Optional unique identifier for order signature

        Returns:
            A dictionary containing a signed order payload with metadata.
        """
        signed = self.sign_order(vendor_id, vendor_order_id, total_amount, valid_until, nonce)
        return {
            "code": "TGETHER_NEEDS_PAYMENT",
            "order": signed["order"],
            "signature": signed["signature"],
            "signer": signed["signer"],
            "contract": self.verifying_contract,
            "chainId": self.chain_id,
            "amount": signed["order"]["totalAmount"],
            "pay_url": pay_url or "https://app.tgether.xyz/pay?vendorOrderId=" + vendor_order_id
        }
