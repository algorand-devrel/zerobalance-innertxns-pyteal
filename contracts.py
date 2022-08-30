#!/usr/bin/env python3

from base64 import b64decode
import json

from algosdk.v2client.algod import AlgodClient
from algosdk.mnemonic import to_private_key, to_public_key
from algosdk.atomic_transaction_composer import AtomicTransactionComposer, TransactionWithSigner, AccountTransactionSigner
from algosdk.future.transaction import ApplicationCreateTxn, ApplicationNoOpTxn, OnComplete, StateSchema
from algosdk.abi.method import Method

from pyteal import *

algod_token = 'a' * 64
algod_server = 'http://127.0.0.1:4001'
algod_client = AlgodClient(algod_token, algod_server)

router = Router("ZeroBalanceInnerTxn")

@router.method(no_op=CallConfig.CREATE)
def deploy() -> Expr:
    return Seq()

@router.method(no_op=CallConfig.CALL)
def message(recipient: abi.Account, message: abi.String) -> Expr:
    return Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: recipient.address(),
                TxnField.amount: Int(0),
                TxnField.fee: Int(0),
                TxnField.note: message.get(),
            }
        ),
        InnerTxnBuilder.Submit(),
    )

@router.method(no_op=CallConfig.CALL)
def call(target_app: abi.Application) -> Expr:
    return Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.MethodCall(
            app_id = target_app.application_id(),
            method_signature="target()void",
            args=[],
            extra_fields={
                TxnField.fee: Int(0),
            }
        ),
        InnerTxnBuilder.Submit(),
    )

approval, clearstate, abi = router.compile_program(version=6)

target_router = Router("Target")

@target_router.method(no_op=CallConfig.CREATE)
def target_deploy() -> Expr:
    return Seq()

@target_router.method(no_op=CallConfig.CALL)
def target() -> Expr:
    return Seq()

target_approval, target_clearstate, target_abi = target_router.compile_program(version=6)

if __name__ == "__main__":
    with open("approval.teal", "w") as f:
        f.write(approval)
    
    with open("clear.teal", "w") as f:
        f.write(clearstate)
    
    with open("abi.json", "w") as f:
        f.write(json.dumps(abi.dictify(), indent=2))

    with open("target_approval.teal", "w") as f:
        f.write(target_approval)
    
    with open("target_clear.teal", "w") as f:
        f.write(target_clearstate)
    
    with open("target_abi.json", "w") as f:
        f.write(json.dumps(target_abi.dictify(), indent=2))
