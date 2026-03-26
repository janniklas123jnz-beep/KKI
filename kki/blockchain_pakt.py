"""
#926 BlockchainPakt — Blockchain: Nakamoto, Smart Contracts & Dezentrale Systeme.
Satoshi Nakamoto (2008): Bitcoin: A Peer-to-Peer Electronic Cash System —
  Blockchain als dezentrales Konsenssystem ohne Vertrauensinstanz; Proof-of-Work.
Buterin (2014): Ethereum Whitepaper — programmierbare Blockchain; Smart Contracts
  als selbstausführende Verträge; Grundlage der dezentralen Finanzwelt (DeFi).
Lamport, Shostak & Pease (1982): Byzantine Generals Problem — Konsensfindung in
  verteilten Systemen bei fehlerhaften Teilnehmern; theoretisches Fundament.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .authentifizierungs_manifest import AuthentifizierungsManifest, build_authentifizierungs_manifest


class BlockchainPaktTyp(Enum):
    PROOF_OF_WORK = auto()
    PROOF_OF_STAKE = auto()
    SMART_CONTRACT = auto()
    DEZENTRALE_FINANZEN = auto()
    NFT_PROTOKOLL = auto()


class BlockchainPaktProzedur(Enum):
    KONSENSBILDUNG = auto()
    VALIDIERUNG = auto()
    MINING = auto()
    STAKING = auto()
    SETTLEMENT = auto()


_WEIGHT_DELTA = {
    BlockchainPaktTyp.PROOF_OF_WORK: 0.0,
    BlockchainPaktTyp.PROOF_OF_STAKE: 1.6,
    BlockchainPaktTyp.SMART_CONTRACT: 3.2,
    BlockchainPaktTyp.DEZENTRALE_FINANZEN: 4.8,
    BlockchainPaktTyp.NFT_PROTOKOLL: 6.4,
}
_TYP_MAP = {
    BlockchainPaktTyp.PROOF_OF_WORK: "proof_of_work",
    BlockchainPaktTyp.PROOF_OF_STAKE: "proof_of_stake",
    BlockchainPaktTyp.SMART_CONTRACT: "smart_contract",
    BlockchainPaktTyp.DEZENTRALE_FINANZEN: "dezentrale_finanzen",
    BlockchainPaktTyp.NFT_PROTOKOLL: "nft_protokoll",
}
_PROZEDUR_MAP = {
    BlockchainPaktProzedur.KONSENSBILDUNG: "konsensbildung",
    BlockchainPaktProzedur.VALIDIERUNG: "validierung",
    BlockchainPaktProzedur.MINING: "mining",
    BlockchainPaktProzedur.STAKING: "staking",
    BlockchainPaktProzedur.SETTLEMENT: "settlement",
}


@dataclass(frozen=True)
class BlockchainPaktEintrag:
    typ: BlockchainPaktTyp
    prozedur: BlockchainPaktProzedur
    cyber_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class BlockchainPakt:
    eintraege: tuple[BlockchainPaktEintrag, ...]
    canonical: bool = True

    def aggregates_pakt_signal(self) -> dict:
        return {
            "pakt_id": "blockchain-pakt-926",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_blockchain_pakt(parent: Optional[AuthentifizierungsManifest] = None) -> BlockchainPakt:
    if parent is None:
        parent = build_authentifizierungs_manifest()
    base = sum(n.cyber_weight for n in parent.normen)
    eintraege = tuple(
        BlockchainPaktEintrag(
            typ=t,
            prozedur=list(BlockchainPaktProzedur)[i],
            cyber_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(BlockchainPaktTyp)
    )
    return BlockchainPakt(eintraege=eintraege)
