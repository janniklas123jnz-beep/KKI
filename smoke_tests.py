"""Leichte Smoke-Tests fuer zentrale KKI-Skripte."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from kki import (
    ActionName,
    ArchiveEntry,
    ArchiveRetention,
    ArchiveStatus,
    ArtifactKind,
    ArtifactScope,
    AutonomyAssignment,
    AutonomyDecision,
    AutonomyGovernor,
    AuthorizationIdentity,
    AuditTrailEntry,
    BenchmarkCase,
    BenchmarkHarness,
    BenchmarkReleaseMode,
    CabinetExecutionMode,
    CabinetOrder,
    CabinetRole,
    CabinetStatus,
    DelegationEntry,
    DelegationLane,
    DelegationMatrix,
    DelegationMode,
    DelegationStatus,
    RecallPath,
    ReleasePath,
    SluiceStatus,
    VetoChannel,
    VetoSluice,
    VetoStop,
    CapacityLane,
    CapacityPlanEntry,
    CapacityPlanner,
    CapacityWindow,
    ChangeWindow,
    ChangeWindowEntry,
    ChangeWindowStatus,
    ClaimStatus,
    ContinuousReadinessCycle,
    ContinuousReadinessIteration,
    ContinuousReadinessStatus,
    ConvergenceProjection,
    ConvergenceSimulator,
    ConvergenceStatus,
    CorrelatedOperation,
    CourseCorrector,
    CourseCorrectionAction,
    CourseCorrectionDirective,
    CourseCorrectionStatus,
    ConsensusDirective,
    ConsensusDirectiveStatus,
    ConsensusDirectiveType,
    ConsensusMandate,
    ConsensusDiplomacy,
    CollegiumLane,
    CollegiumMandate,
    CollegiumSeat,
    CollegiumStatus,
    ConclaveLane,
    ConclaveMotion,
    ConclavePriority,
    ConclaveStatus,
    ContractClause,
    ContractCommitment,
    ContractParty,
    ContractStatus,
    CodexAxis,
    CodexCanon,
    CodexSection,
    CodexStatus,
    KodexRegister,
    KodexRegisterEntry,
    RatBench,
    RatInterpretation,
    RatStatus,
    SatzungsRat,
    SatzungsRatArticle,
    KonventEbene,
    KonventMandat,
    KonventStatus,
    MandatsKonvent,
    MandatsLinie,
    NormenTribunal,
    TribunalFall,
    TribunalKammer,
    TribunalUrteil,
    TribunalVerfahren,
    build_normen_tribunal,
    SenatsBeschluss,
    SenatsFraktion,
    SenatsSitzung,
    SenatsMandat,
    VerfassungsSenat,
    build_verfassungs_senat,
    ChartaArtikel,
    ChartaGeltung,
    ChartaKapitel,
    ChartaVerfahren,
    GrundrechtsCharta,
    build_grundrechts_charta,
    AktKlausel,
    AktProzedur,
    AktSektion,
    AktStatus,
    SouveraenitaetsAkt,
    build_souveraenitaets_akt,
    ManifestAbschnitt,
    ManifestGeltung,
    ManifestKapitel,
    ManifestVerfahren,
    OrdnungsManifest,
    build_ordnungs_manifest,
    Leitordnung,
    OrdnungsKraft,
    OrdnungsNorm,
    OrdnungsRang,
    build_leitordnung,
    AutoritaetsDekret,
    DekretGeltung,
    DekretKlausel,
    DekretProzedur,
    DekretSektion,
    build_autoritaets_dekret,
    FundamentKraft,
    FundamentPfeiler,
    FundamentSaeule,
    FundamentVerfahren,
    RechtsFundament,
    build_rechts_fundament,
    GrundsatzRegister,
    RegisterEintrag,
    RegisterKategorie,
    RegisterProzedur,
    RegisterStatus,
    build_grundsatz_register,
    PrinzipienKlasse,
    PrinzipienKodex,
    PrinzipienProzedur,
    PrinzipienSatz,
    PrinzipienStatus,
    build_prinzipien_kodex,
    WerteArtikel,
    WerteCharta,
    WerteProzedur,
    WerteStatus,
    WerteTyp,
    build_werte_charta,
    KonventBeschluss,
    KonventProzedur,
    LeitbildAusrichtung,
    LeitbildKonvent,
    LeitbildResolution,
    build_leitbild_konvent,
    MissionsArtikel,
    MissionsRang,
    MissionsVerfassung,
    VerfassungsProzedur,
    VerfassungsStatus,
    build_missions_verfassung,
    ManifestGeltung,
    ManifestProzedur,
    ZweckDimension,
    ZweckKlausel,
    ZweckManifest,
    build_zweck_manifest,
    KonstitutionsArtikel,
    KonstitutionsEbene,
    KonstitutionsProzedur,
    KonstitutionsRang,
    LeitsternKonstitution,
    build_leitstern_konstitution,
    GrundgesetzGeltung,
    GrundgesetzParagraph,
    GrundgesetzProzedur,
    GrundgesetzTitel,
    VerfassungsGrundgesetz,
    build_verfassungs_grundgesetz,
    StaatsEbene,
    StaatsGeltung,
    StaatsNorm,
    StaatsOrdnung,
    StaatsProzedur,
    build_staats_ordnung,
    KodexKlasse,
    KodexNorm,
    KodexProzedur,
    KodexStatus,
    RechtsKodex,
    build_rechts_kodex,
    UnionsAkt,
    UnionsGeltung,
    UnionsNorm,
    UnionsProzedur,
    UnionsTyp,
    build_unions_akt,
    FoederalGeltung,
    FoederalNorm,
    FoederalProzedur,
    FoederalTyp,
    FoederalVertrag,
    build_foederal_vertrag,
    BundesCharta,
    BundesGeltung,
    BundesNorm,
    BundesProzedur,
    BundesRang,
    build_bundes_charta,
    HoheitsGeltung,
    HoheitsGrad,
    HoheitsManifest,
    HoheitsNorm,
    HoheitsProzedur,
    build_hoheits_manifest,
    SuprematsGeltung,
    SuprematsKlasse,
    SuprematsNorm,
    SuprematsProzedur,
    SuprematsRegister,
    build_supremats_register,
    EwigkeitsEintrag,
    EwigkeitsGeltung,
    EwigkeitsNorm,
    EwigkeitsProzedur,
    EwigkeitsTyp,
    build_ewigkeits_norm,
    GrundrechtsSenat,
    SenatGeltung,
    SenatNorm,
    SenatProzedur,
    SenatRang,
    build_grundrechts_senat,
    VerfassungsKodex,
    VerfassungsKodexGeltung,
    VerfassungsKodexNorm,
    VerfassungsKodexProzedur,
    VerfassungsKodexRang,
    build_verfassungs_kodex,
    AllianzGeltung,
    AllianzNorm,
    AllianzProzedur,
    AllianzTyp,
    AllianzVertrag,
    build_allianz_vertrag,
    KooperationsGeltung,
    KooperationsGrad,
    KooperationsManifest,
    KooperationsNorm,
    KooperationsProzedur,
    build_kooperations_manifest,
    SolidaritaetsGeltung,
    SolidaritaetsNorm,
    SolidaritaetsPakt,
    SolidaritaetsProzedur,
    SolidaritaetsTyp,
    build_solidaritaets_pakt,
    UniversalrechtsGeltung,
    UniversalrechtsNorm,
    UniversalrechtsProzedur,
    UniversalrechtsRang,
    UniversalrechtsRegister,
    build_universalrechts_register,
    EwigkeitsEintrag,
    EwigkeitsGeltung,
    EwigkeitsNorm,
    EwigkeitsProzedur,
    EwigkeitsTyp,
    build_ewigkeits_norm,
    EinheitsGeltung,
    EinheitsNorm,
    EinheitsProzedur,
    EinheitsSenat,
    EinheitsTyp,
    build_einheits_senat,
    HarmonieGeltung,
    HarmonieNorm,
    HarmoniePakt,
    HarmonieProzedur,
    HarmonieTyp,
    build_harmonie_pakt,
    KosmosOrdnung,
    KosmosOrdnungsGeltung,
    KosmosOrdnungsNorm,
    KosmosOrdnungsProzedur,
    KosmosOrdnungsTyp,
    build_kosmos_ordnung,
    KosmosEwigkeit,
    KosmosEwigkeitsGeltung,
    KosmosEwigkeitsNormEintrag,
    KosmosEwigkeitsProzedur,
    KosmosEwigkeitsRang,
    build_kosmos_ewigkeit,
    AbsolutCharta,
    AbsolutGeltung,
    AbsolutNorm,
    AbsolutProzedur,
    AbsolutTyp,
    build_absolut_charta,
    KosmosVerfassung,
    KosmosVerfassungsGeltung,
    KosmosVerfassungsNorm,
    KosmosVerfassungsProzedur,
    KosmosVerfassungsTyp,
    build_kosmos_verfassung,
    QuantenFeld,
    QuantenFeldGeltung,
    QuantenFeldNorm,
    QuantenFeldProzedur,
    QuantenFeldTyp,
    build_quanten_feld,
    DimensionsGeltung,
    DimensionsNorm,
    DimensionsProzedur,
    DimensionsRang,
    DimensionsRegister,
    build_dimensions_register,
    WellenCharta,
    WellenGeltung,
    WellenNorm,
    WellenProzedur,
    WellenTyp,
    build_wellen_charta,
    SuperpositionsGeltung,
    SuperpositionsKodex,
    SuperpositionsNorm,
    SuperpositionsProzedur,
    SuperpositionsTyp,
    build_superpositions_kodex,
    VerschraenkunsGeltung,
    VerschraenkunsNorm,
    VerschraenkunsPakt,
    VerschraenkunsProzedur,
    VerschraenkunsTyp,
    build_verschraenkungs_pakt,
    KollapsGeltung,
    KollapsManifest,
    KollapsNorm,
    KollapsProzedur,
    KollapsTyp,
    build_kollaps_manifest,
    QuantenSenat,
    QuantenSenatGeltung,
    QuantenSenatNorm,
    QuantenSenatProzedur,
    QuantenSenatTyp,
    build_quanten_senat,
    PlanckGeltung,
    PlanckNorm,
    PlanckNormEintrag,
    PlanckProzedur,
    PlanckTyp,
    build_planck_norm,
    StringtheorieCharta,
    StringtheorieGeltung,
    StringtheorieNorm,
    StringtheorieProzedur,
    StringtheorieTyp,
    build_stringtheorie_charta,
    QuantenVerfassung,
    QuantenVerfassungsGeltung,
    QuantenVerfassungsNorm,
    QuantenVerfassungsProzedur,
    QuantenVerfassungsTyp,
    build_quanten_verfassung,
    RelativitaetsFeld,
    RelativitaetsGeltung,
    RelativitaetsNorm,
    RelativitaetsProzedur,
    RelativitaetsTyp,
    build_relativitaets_feld,
    RaumzeitGeltung,
    RaumzeitNorm,
    RaumzeitProzedur,
    RaumzeitRang,
    RaumzeitRegister,
    build_raumzeit_register,
    LichtgeschwindigkeitsCharta,
    LichtgeschwindigkeitsGeltung,
    LichtgeschwindigkeitsNorm,
    LichtgeschwindigkeitsProzedur,
    LichtgeschwindigkeitsTyp,
    build_lichtgeschwindigkeits_charta,
    GravitationsGeltung,
    GravitationsKodex,
    GravitationsNorm,
    GravitationsProzedur,
    GravitationsTyp,
    build_gravitations_kodex,
    KruemmungsGeltung,
    KruemmungsNorm,
    KruemmungsPakt,
    KruemmungsProzedur,
    KruemmungsTyp,
    build_kruemmungs_pakt,
    SingularitaetsGeltung,
    SingularitaetsManifest,
    SingularitaetsNorm,
    SingularitaetsProzedur,
    SingularitaetsTyp,
    build_singularitaets_manifest,
    SchwarzeLoechSenat,
    SchwarzsLochGeltung,
    SchwarzsLochNorm,
    SchwarzsLochProzedur,
    SchwarzsLochTyp,
    build_schwarzes_loch_senat,
    EreignishorizontGeltung,
    EreignishorizontNorm,
    EreignishorizontNormEintrag,
    EreignishorizontProzedur,
    EreignishorizontTyp,
    build_ereignishorizont_norm,
    ZeitdilatationsCharta,
    ZeitdilatationsGeltung,
    ZeitdilatationsNorm,
    ZeitdilatationsProzedur,
    ZeitdilatationsTyp,
    build_zeitdilatations_charta,
    RelativitaetsGeltung,
    RelativitaetsNorm,
    RelativitaetsProzedur,
    RelativitaetsTyp,
    RelativitaetsVerfassung,
    build_relativitaets_verfassung,
    ThermodynamikFeld,
    ThermodynamikGeltung,
    ThermodynamikNorm,
    ThermodynamikProzedur,
    ThermodynamikTyp,
    build_thermodynamik_feld,
    EntropieGeltung,
    EntropieNorm,
    EntropieRegister,
    EntropieProzedur,
    EntropieTyp,
    build_entropie_register,
    WaermeCharta,
    WaermeGeltung,
    WaermeNorm,
    WaermeProzedur,
    WaermeTyp,
    build_waerme_charta,
    EnergieerhaltungsGeltung,
    EnergieerhaltungsKodex,
    EnergieerhaltungsNorm,
    EnergieerhaltungsProzedur,
    EnergieerhaltungsTyp,
    build_energieerhaltungs_kodex,
    GleichgewichtsGeltung,
    GleichgewichtsNorm,
    GleichgewichtsPakt,
    GleichgewichtsProzedur,
    GleichgewichtsTyp,
    build_gleichgewichts_pakt,
    CarnotGeltung,
    CarnotManifest,
    CarnotNorm,
    CarnotProzedur,
    CarnotTyp,
    build_carnot_manifest,
    BoltzmannGeltung,
    BoltzmannNorm,
    BoltzmannSenat,
    BoltzmannProzedur,
    BoltzmannTyp,
    build_boltzmann_senat,
    EntropieNormEintrag,
    EntropieNormGeltung,
    EntropieNormProzedur,
    EntropieNormSatz,
    EntropieNormTyp,
    build_entropie_norm,
    WaermestrahlungsCharta,
    WaermestrahlungsGeltung,
    WaermestrahlungsNorm,
    WaermestrahlungsProzedur,
    WaermestrahlungsTyp,
    build_waermestrahlung_charta,
    ThermodynamikVerfassung,
    ThermoverfassungsGeltung,
    ThermoverfassungsNorm,
    ThermoverfassungsProzedur,
    ThermoverfassungsTyp,
    build_thermodynamik_verfassung,
    ElektromagnetikFeld,
    ElektromagnetikGeltung,
    ElektromagnetikNorm,
    ElektromagnetikProzedur,
    ElektromagnetikTyp,
    build_elektromagnetik_feld,
    LadungsGeltung,
    LadungsNorm,
    LadungsProzedur,
    LadungsRegister,
    LadungsTyp,
    build_ladungs_register,
    MaxwellCharta,
    MaxwellGeltung,
    MaxwellNorm,
    MaxwellProzedur,
    MaxwellTyp,
    build_maxwell_charta,
    InduktionsGeltung,
    InduktionsKodex,
    InduktionsNorm,
    InduktionsProzedur,
    InduktionsTyp,
    build_induktions_kodex,
    WellenausbreitungsGeltung,
    WellenausbreitungsNorm,
    WellenausbreitungsPakt,
    WellenausbreitungsProzedur,
    WellenausbreitungsTyp,
    build_wellenausbreitung_pakt,
    LichtgeschwindigkeitsGeltung,
    LichtgeschwindigkeitsManifest,
    LichtgeschwindigkeitsNorm,
    LichtgeschwindigkeitsProzedur,
    LichtgeschwindigkeitsTyp,
    build_lichtgeschwindigkeits_manifest,
    SpektralGeltung,
    SpektralNorm,
    SpektralProzedur,
    SpektralSenat,
    SpektralTyp,
    build_spektral_senat,
    PhotonNormEintrag,
    PhotonNormGeltung,
    PhotonNormProzedur,
    PhotonNormSatz,
    PhotonNormTyp,
    build_photon_norm,
    PhotoeffektCharta,
    PhotoeffektGeltung,
    PhotoeffektNorm,
    PhotoeffektProzedur,
    PhotoeffektTyp,
    build_photoeffekt_charta,
    ElektromagnetikVerfassung,
    ElektroverfassungsGeltung,
    ElektroverfassungsNorm,
    ElektroverfassungsProzedur,
    ElektroverfassungsTyp,
    build_elektromagnetik_verfassung,
    KernphysikFeld,
    KernphysikGeltung,
    KernphysikNorm,
    KernphysikProzedur,
    KernphysikTyp,
    build_kernphysik_feld,
    NukleonGeltung,
    NukleonNorm,
    NukleonProzedur,
    NukleonRegister,
    NukleonTyp,
    build_nukleon_register,
    StarkCharta,
    StarkGeltung,
    StarkNorm,
    StarkProzedur,
    StarkTyp,
    build_stark_charta,
    SchwachGeltung,
    SchwachKodex,
    SchwachNorm,
    SchwachProzedur,
    SchwachTyp,
    build_schwach_kodex,
    KernspaltungsGeltung,
    KernspaltungsNorm,
    KernspaltungsPakt,
    KernspaltungsProzedur,
    KernspaltungsTyp,
    build_kernspaltungs_pakt,
    KernfusionsGeltung,
    KernfusionsManifest,
    KernfusionsNorm,
    KernfusionsProzedur,
    KernfusionsTyp,
    build_kernfusions_manifest,
    RadioaktivitaetsGeltung,
    RadioaktivitaetsNorm,
    RadioaktivitaetsProzedur,
    RadioaktivitaetsSenat,
    RadioaktivitaetsTyp,
    build_radioaktivitaets_senat,
    ZerfallsNormEintrag,
    ZerfallsNormGeltung,
    ZerfallsNormProzedur,
    ZerfallsNormSatz,
    ZerfallsNormTyp,
    build_zerfalls_norm,
    NuklearCharta,
    NuklearChartaGeltung,
    NuklearChartaNorm,
    NuklearChartaProzedur,
    NuklearChartaTyp,
    build_nuklear_charta,
    KernphysikVerfassung,
    KernphysikVerfassungsGeltung,
    KernphysikVerfassungsNorm,
    KernphysikVerfassungsProzedur,
    KernphysikVerfassungsTyp,
    build_kernphysik_verfassung,
    TeilchenFeld,
    TeilchenGeltung,
    TeilchenNorm,
    TeilchenProzedur,
    TeilchenTyp,
    build_teilchen_feld,
    QuarkGeltung,
    QuarkNorm,
    QuarkProzedur,
    QuarkRegister,
    QuarkTyp,
    build_quark_register,
    LeptonCharta,
    LeptonGeltung,
    LeptonNorm,
    LeptonProzedur,
    LeptonTyp,
    build_lepton_charta,
    GluonGeltung,
    GluonKodex,
    GluonNorm,
    GluonProzedur,
    GluonTyp,
    build_gluon_kodex,
    EichbosonGeltung,
    EichbosonNorm,
    EichbosonPakt,
    EichbosonProzedur,
    EichbosonTyp,
    build_eichboson_pakt,
    HiggsGeltung,
    HiggsManifest,
    HiggsNorm,
    HiggsProzedur,
    HiggsTyp,
    build_higgs_manifest,
    SymmetriebrechungsGeltung,
    SymmetriebrechungsNorm,
    SymmetriebrechungsProzedur,
    SymmetriebrechungsSenat,
    SymmetriebrechungsTyp,
    build_symmetriebrechungs_senat,
    FeynmanNormEintrag,
    FeynmanNormGeltung,
    FeynmanNormProzedur,
    FeynmanNormSatz,
    FeynmanNormTyp,
    build_feynman_norm,
    StandardmodellCharta,
    StandardmodellGeltung,
    StandardmodellNorm,
    StandardmodellProzedur,
    StandardmodellTyp,
    build_standardmodell_charta,
    TeilchenphysikGeltung,
    TeilchenphysikNorm,
    TeilchenphysikProzedur,
    TeilchenphysikTyp,
    TeilchenphysikVerfassung,
    build_teilchenphysik_verfassung,
    KosmologieFeld,
    KosmologieGeltung,
    KosmologieNorm,
    KosmologieProzedur,
    KosmologieTyp,
    build_kosmologie_feld,
    UrknallGeltung,
    UrknallNorm,
    UrknallProzedur,
    UrknallRegister,
    UrknallTyp,
    build_urknall_register,
    InflationCharta,
    InflationGeltung,
    InflationNorm,
    InflationProzedur,
    InflationTyp,
    build_inflation_charta,
    DunkleMaterieGeltung,
    DunkleMaterieKodex,
    DunkleMaterieNorm,
    DunkleMaterieProzedue,
    DunkleMaterieTyp,
    build_dunkle_materie_kodex,
    DunkleEnergieGeltung,
    DunkleEnergieNorm,
    DunkleEnergiePakt,
    DunkleEnergieProzedur,
    DunkleEnergieTyp,
    build_dunkle_energie_pakt,
    CmbGeltung,
    CmbManifest,
    CmbNorm,
    CmbProzedur,
    CmbTyp,
    build_cmb_manifest,
    StrukturbildungsGeltung,
    StrukturbildungsNorm,
    StrukturbildungsProzedur,
    StrukturbildungsSenat,
    StrukturbildungsTyp,
    build_strukturbildungs_senat,
    ExpansionNormEintrag,
    ExpansionNormGeltung,
    ExpansionNormProzedur,
    ExpansionNormSatz,
    ExpansionNormTyp,
    build_expansion_norm,
    HubbleCharta,
    HubbleGeltung,
    HubbleNorm,
    HubbleProzedur,
    HubbleTyp,
    build_hubble_charta,
    KosmologieVerfassung,
    KosmologieVerfassungsGeltung,
    KosmologieVerfassungsNorm,
    KosmologieVerfassungsProzedur,
    KosmologieVerfassungsTyp,
    build_kosmologie_verfassung,
    AstrophysikFeld,
    AstrophysikGeltung,
    AstrophysikNorm,
    AstrophysikProzedur,
    AstrophysikTyp,
    build_astrophysik_feld,
    ProtostellarGeltung,
    ProtostellarNorm,
    ProtostellarProzedur,
    ProtostellarRegister,
    ProtostellarTyp,
    build_protostellar_register,
    HauptreihenchartaCharta,
    HauptreihenchartaGeltung,
    HauptreihenchartaNorm,
    HauptreihenchartaProzedur,
    HauptreihenchartaTyp,
    build_hauptreihen_charta,
    FusionsreaktorGeltung,
    FusionsreaktorKodex,
    FusionsreaktorNorm,
    FusionsreaktorProzedur,
    FusionsreaktorTyp,
    build_fusionsreaktor_kodex,
    RoterRieseGeltung,
    RoterRieseNorm,
    RoterRiesePakt,
    RoterRieseProzedur,
    RoterRieseTyp,
    build_roter_riese_pakt,
    SupernovaGeltung,
    SupernovaManifest,
    SupernovaNorm,
    SupernovaProzedur,
    SupernovaTyp,
    build_supernova_manifest,
    NeutronensternGeltung,
    NeutronensternNorm,
    NeutronensternProzedur,
    NeutronensternSenat,
    NeutronensternTyp,
    build_neutronenstern_senat,
    SchwarzerLochNormEintrag,
    SchwarzerLochNormGeltung,
    SchwarzerLochNormProzedur,
    SchwarzerLochNormSatz,
    SchwarzerLochNormTyp,
    build_schwarzes_loch_norm,
    HertzsprungRussellCharta,
    HertzsprungRussellGeltung,
    HertzsprungRussellNorm,
    HertzsprungRussellProzedur,
    HertzsprungRussellTyp,
    build_hertzsprung_russell_charta,
    AstrophysikVerfassung,
    AstrophysikVerfassungsGeltung,
    AstrophysikVerfassungsNorm,
    AstrophysikVerfassungsProzedur,
    AstrophysikVerfassungsTyp,
    build_astrophysik_verfassung,
    FestkoerperFeld,
    FestkoerperGeltung,
    FestkoerperNorm,
    FestkoerperProzedur,
    FestkoerperTyp,
    build_festkoerper_feld,
    KristallgitterRegister,
    KristallgitterGeltung,
    KristallgitterNorm,
    KristallgitterProzedur,
    KristallgitterTyp,
    build_kristallgitter_register,
    BandstrukturCharta,
    BandstrukturGeltung,
    BandstrukturNorm,
    BandstrukturProzedur,
    BandstrukturTyp,
    build_bandstruktur_charta,
    HalbleiterKodex,
    HalbleiterGeltung,
    HalbleiterNorm,
    HalbleiterProzedur,
    HalbleiterTyp,
    build_halbleiter_kodex,
    SupraleitungPakt,
    SupraleitungGeltung,
    SupraleitungNorm,
    SupraleitungProzedur,
    SupraleitungTyp,
    build_supraleitung_pakt,
    QuantenHallManifest,
    QuantenHallGeltung,
    QuantenHallNorm,
    QuantenHallProzedur,
    QuantenHallTyp,
    build_quanten_hall_manifest,
    PhononSenat,
    PhononGeltung,
    PhononNorm,
    PhononProzedur,
    PhononTyp,
    build_phonon_senat,
    FermiNormSatz,
    FermiNormEintrag,
    FermiNormGeltung,
    FermiNormProzedur,
    FermiNormTyp,
    build_fermi_norm,
    BoseEinsteinCharta,
    BoseEinsteinGeltung,
    BoseEinsteinNorm,
    BoseEinsteinProzedur,
    BoseEinsteinTyp,
    build_bose_einstein_charta,
    FestkoerperVerfassung,
    FestkoerperVerfassungsGeltung,
    FestkoerperVerfassungsNorm,
    FestkoerperVerfassungsProzedur,
    FestkoerperVerfassungsTyp,
    build_festkoerper_verfassung,
    PlasmaFeld,
    PlasmaGeltung,
    PlasmaNorm,
    PlasmaProzedur,
    PlasmaTyp,
    build_plasma_feld,
    MagnetohydrodynamikGeltung,
    MagnetohydrodynamikNorm,
    MagnetohydrodynamikProzedur,
    MagnetohydrodynamikRegister,
    MagnetohydrodynamikTyp,
    build_magnetohydrodynamik_register,
    DebyeAbschirmungCharta,
    DebyeAbschirmungGeltung,
    DebyeAbschirmungNorm,
    DebyeAbschirmungProzedur,
    DebyeAbschirmungTyp,
    build_debye_abschirmung_charta,
    AlfvenWellenGeltung,
    AlfvenWellenKodex,
    AlfvenWellenNorm,
    AlfvenWellenProzedur,
    AlfvenWellenTyp,
    build_alfven_wellen_kodex,
    ZPinchGeltung,
    ZPinchNorm,
    ZPinchPakt,
    ZPinchProzedur,
    ZPinchTyp,
    build_z_pinch_pakt,
    TokamakGeltung,
    TokamakManifest,
    TokamakNorm,
    TokamakProzedur,
    TokamakTyp,
    build_tokamak_manifest,
    TraegheitsfusionGeltung,
    TraegheitsfusionNorm,
    TraegheitsfusionProzedur,
    TraegheitsfusionSenat,
    TraegheitsfusionTyp,
    build_traegheitsfusion_senat,
    PlasmaWellenNormEintrag,
    PlasmaWellenNormGeltung,
    PlasmaWellenNormProzedur,
    PlasmaWellenNormSatz,
    PlasmaWellenNormTyp,
    build_plasmawellen_norm,
    KernfusionCharta,
    KernfusionGeltung,
    KernfusionNorm,
    KernfusionProzedur,
    KernfusionTyp,
    build_kernfusion_charta,
    PlasmaVerfassung,
    PlasmaVerfassungsGeltung,
    PlasmaVerfassungsNorm,
    PlasmaVerfassungsProzedur,
    PlasmaVerfassungsTyp,
    build_plasma_verfassung,
    LorenzAttraktorFeld,
    LorenzAttraktorGeltung,
    LorenzAttraktorNorm,
    LorenzAttraktorProzedur,
    LorenzAttraktorTyp,
    build_lorenz_attraktor_feld,
    BifurkationsGeltung,
    BifurkationsNorm,
    BifurkationsProzedur,
    BifurkationsRegister,
    BifurkationsTyp,
    build_bifurkations_register,
    LyapunovGeltung,
    LyapunovKodex,
    LyapunovNorm,
    LyapunovProzedur,
    LyapunovTyp,
    build_lyapunov_kodex,
    FraktalCharta,
    FraktalGeltung,
    FraktalNorm,
    FraktalProzedur,
    FraktalTyp,
    build_fraktal_charta,
    StrangeAttraktorGeltung,
    StrangeAttraktorNorm,
    StrangeAttraktorPakt,
    StrangeAttraktorProzedur,
    StrangeAttraktorTyp,
    build_strange_attraktor_pakt,
    EmergenzGeltung,
    EmergenzNorm,
    EmergenzProzedur,
    EmergenzSenat,
    EmergenzTyp,
    build_emergenz_senat,
    PerkolationsNormEintrag,
    PerkolationsNormGeltung,
    PerkolationsNormProzedur,
    PerkolationsNormSatz,
    PerkolationsNormTyp,
    build_perkolations_norm,
    KomplexitaetsCharta,
    KomplexitaetsGeltung,
    KomplexitaetsNorm,
    KomplexitaetsProzedur,
    KomplexitaetsTyp,
    build_komplexitaets_charta,
    AdaptivSchwarmGeltung,
    AdaptivSchwarmKodex,
    AdaptivSchwarmNorm,
    AdaptivSchwarmProzedur,
    AdaptivSchwarmTyp,
    build_adaptiv_schwarm_kodex,
    ChaosVerfassung,
    ChaosVerfassungsGeltung,
    ChaosVerfassungsNorm,
    ChaosVerfassungsProzedur,
    ChaosVerfassungsTyp,
    build_chaos_verfassung,
    ShannonEntropieFeld,
    ShannonEntropieGeltung,
    ShannonEntropieNorm,
    ShannonEntropieProzedur,
    ShannonEntropieTyp,
    build_shannon_entropie_feld,
    KanalkapazitaetGeltung,
    KanalkapazitaetNorm,
    KanalkapazitaetProzedur,
    KanalkapazitaetRegister,
    KanalkapazitaetTyp,
    build_kanalkapazitaet_register,
    QuantenBitGeltung,
    QuantenBitKodex,
    QuantenBitNorm,
    QuantenBitProzedur,
    QuantenBitTyp,
    build_quanten_bit_kodex,
    VerschraenkungCharta,
    VerschraenkungGeltung,
    VerschraenkungNorm,
    VerschraenkungProzedur,
    VerschraenkungTyp,
    build_verschraenkung_charta,
    QuantenfehlerGeltung,
    QuantenfehlerNorm,
    QuantenfehlerPakt,
    QuantenfehlerProzedur,
    QuantenfehlerTyp,
    build_quantenfehler_pakt,
    QuantenkryptoGeltung,
    QuantenkryptoNorm,
    QuantenkryptoProzedur,
    QuantenkryptoSenat,
    QuantenkryptoTyp,
    build_quantenkrypto_senat,
    HolographischesPrinzipNormEintrag,
    HolographischesPrinzipNormGeltung,
    HolographischesPrinzipNormProzedur,
    HolographischesPrinzipNormSatz,
    HolographischesPrinzipNormTyp,
    build_holographisches_prinzip_norm,
    LandauerGeltung,
    LandauerManifest,
    LandauerNorm,
    LandauerProzedur,
    LandauerTyp,
    build_landauer_manifest,
    NoCloningGeltung,
    NoCloningKodex,
    NoCloningNorm,
    NoCloningProzedur,
    NoCloningTyp,
    build_no_cloning_kodex,
    QuanteninformationsVerfassung,
    QuanteninformationsVerfassungsGeltung,
    QuanteninformationsVerfassungsNorm,
    QuanteninformationsVerfassungsProzedur,
    QuanteninformationsVerfassungsTyp,
    build_quanteninformations_verfassung,
    BiophysikFeld,
    BiophysikGeltung,
    BiophysikNorm,
    BiophysikProzedur,
    BiophysikTyp,
    build_biophysik_feld,
    DnaReplikationGeltung,
    DnaReplikationNorm,
    DnaReplikationProzedur,
    DnaReplikationRegister,
    DnaReplikationTyp,
    build_dna_replikation_register,
    ProteinfaltungCharta,
    ProteinfaltungGeltung,
    ProteinfaltungNorm,
    ProteinfaltungProzedur,
    ProteinfaltungTyp,
    build_proteinfaltung_charta,
    HodgkinHuxleyGeltung,
    HodgkinHuxleyKodex,
    HodgkinHuxleyNorm,
    HodgkinHuxleyProzedur,
    HodgkinHuxleyTyp,
    build_hodgkin_huxley_kodex,
    SynaptischePlastizitaetGeltung,
    SynaptischePlastizitaetNorm,
    SynaptischePlastizitaetPakt,
    SynaptischePlastizitaetProzedur,
    SynaptischePlastizitaetTyp,
    build_synaptische_plastizitaet_pakt,
    EvolutionGeltung,
    EvolutionManifest,
    EvolutionNorm,
    EvolutionProzedur,
    EvolutionTyp,
    build_evolution_manifest,
    HomoostaseGeltung,
    HomoostaseNorm,
    HomoostaseSenat,
    HomoostaseTyp,
    HomoostasProzedur,
    build_homoostase_senat,
    LotkaVolterraNormEintrag,
    LotkaVolterraNormGeltung,
    LotkaVolterraNormProzedur,
    LotkaVolterraNormSatz,
    LotkaVolterraNormTyp,
    build_lotka_volterra_norm,
    MorphogeneseCharta,
    MorphogeneseGeltung,
    MorphogeneseNorm,
    MorphogeneseProzedur,
    MorphogeneseTyp,
    build_morphogenese_charta,
    SystembiologieVerfassung,
    SystembiologieVerfassungsGeltung,
    SystembiologieVerfassungsNorm,
    SystembiologieVerfassungsProzedur,
    SystembiologieVerfassungsTyp,
    build_systembiologie_verfassung,
    KognitionsFeld,
    KognitionsGeltung,
    KognitionsNorm,
    KognitionsProzedur,
    KognitionsTyp,
    build_kognitions_feld,
    ArbeitsgedaechtnisGeltung,
    ArbeitsgedaechtnisNorm,
    ArbeitsgedaechtnisRegister,
    ArbeitsgedaechtnisTyp,
    ArbeitsgedaechtnispProzedur,
    build_arbeitsgedaechtnis_register,
    AufmerksamkeitsCharta,
    AufmerksamkeitsGeltung,
    AufmerksamkeitsNorm,
    AufmerksamkeitsProzedur,
    AufmerksamkeitsTyp,
    build_aufmerksamkeits_charta,
    EntscheidungsGeltung,
    EntscheidungsKodex,
    EntscheidungsNorm,
    EntscheidungsProzedur,
    EntscheidungsTyp,
    build_entscheidungs_kodex,
    GedaechtnisKonsolidierungsGeltung,
    GedaechtnisKonsolidierungsNorm,
    GedaechtnisKonsolidierungsPakt,
    GedaechtnisKonsolidierungsProzedur,
    GedaechtnisKonsolidierungsTyp,
    build_gedaechtnis_konsolidierungs_pakt,
    SprachverarbeitungsGeltung,
    SprachverarbeitungsManifest,
    SprachverarbeitungsNorm,
    SprachverarbeitungsProzedur,
    SprachverarbeitungsTyp,
    build_sprachverarbeitungs_manifest,
    BewusstseinsGeltung,
    BewusstseinsNorm,
    BewusstseinsSenat,
    BewusstseinsTyp,
    BewusstseinsProzedur,
    build_bewusstseins_senat,
    MetakognitionsNormEintrag,
    MetakognitionsNormGeltung,
    MetakognitionsNormProzedur,
    MetakognitionsNormSatz,
    MetakognitionsNormTyp,
    build_metakognitions_norm,
    KognitiveFlexibilitaetsCharta,
    KognitiveFlexibilitaetsGeltung,
    KognitiveFlexibilitaetsNorm,
    KognitiveFlexibilitaetsProzedur,
    KognitiveFlexibilitaetsTyp,
    build_kognitive_flexibilitaets_charta,
    KognitionsVerfassung,
    KognitionsVerfassungsGeltung,
    KognitionsVerfassungsNorm,
    KognitionsVerfassungsProzedur,
    KognitionsVerfassungsTyp,
    build_kognitions_verfassung,
)
from kki.mathematik_feld import (
    MathematikFeld, MathematikFeldGeltung, MathematikFeldNorm,
    MathematikFeldTyp, MathematikFeldProzedur, build_mathematik_feld,
)
from kki.mengen_register import (
    MengenRegister, MengenRegisterGeltung, MengenRegisterNorm,
    MengenRegisterTyp, MengenRegisterProzedur, build_mengen_register,
)
from kki.logik_charta import (
    LogikCharta, LogikChartaGeltung, LogikChartaNorm,
    LogikChartaTyp, LogikChartaProzedur, build_logik_charta,
)
from kki.wahrscheinlichkeits_kodex import (
    WahrscheinlichkeitsKodex, WahrscheinlichkeitsKodexGeltung, WahrscheinlichkeitsKodexNorm,
    WahrscheinlichkeitsKodexTyp, WahrscheinlichkeitsKodexProzedur, build_wahrscheinlichkeits_kodex,
)
from kki.spieltheorie_pakt import (
    SpieltheoriePakt, SpieltheoriePaktGeltung, SpieltheoriePaktNorm,
    SpieltheoriePaktTyp, SpieltheoriePaktProzedur, build_spieltheorie_pakt,
)
from kki.graphen_manifest import (
    GraphenManifest, GraphenManifestGeltung, GraphenManifestNorm,
    GraphenManifestTyp, GraphenManifestProzedur, build_graphen_manifest,
)
from kki.algorithmen_senat import (
    AlgorithmenSenat, AlgorithmenSenatGeltung, AlgorithmenSenatNorm,
    AlgorithmenSenatTyp, AlgorithmenSenatProzedur, build_algorithmen_senat,
)
from kki.godel_norm import (
    GodelNormSatz, GodelNormGeltung, GodelNormEintrag,
    GodelNormTyp, GodelNormProzedur, build_godel_norm,
)
from kki.topologie_charta import (
    TopologieCharta, TopologieChartaGeltung, TopologieChartaNorm,
    TopologieChartaTyp, TopologieChartaProzedur, build_topologie_charta,
)
from kki.mathematik_verfassung import (
    MathematikVerfassung, MathematikVerfassungsGeltung, MathematikVerfassungsNorm,
    MathematikVerfassungsTyp, MathematikVerfassungsProzedur, build_mathematik_verfassung,
)
from kki.emergenz_feld import (
    EmergenzFeld, EmergenzFeldGeltung, EmergenzFeldNorm,
    EmergenzFeldTyp, EmergenzFeldProzedur, build_emergenz_feld,
)
from kki.dissipative_strukturen_register import (
    DissipativeStrukturenRegister, DissipativeStrukturenRegisterGeltung, DissipativeStrukturenRegisterNorm,
    DissipativeStrukturenRegisterTyp, DissipativeStrukturenRegisterProzedur, build_dissipative_strukturen_register,
)
from kki.kritikalitaets_charta import (
    KritikalitaetsCharta, KritikalitaetsChartaGeltung, KritikalitaetsChartaNorm,
    KritikalitaetsChartaTyp, KritikalitaetsChartaProzedur, build_kritikalitaets_charta,
)
from kki.fraktal_kodex import (
    FraktalKodex, FraktalKodexGeltung, FraktalKodexNorm,
    FraktalKodexTyp, FraktalKodexProzedur, build_fraktal_kodex,
)
from kki.zellulaere_automaten_pakt import (
    ZellulaereAutomatenPakt, ZellulaereAutomatenPaktGeltung, ZellulaereAutomatenPaktNorm,
    ZellulaereAutomatenPaktTyp, ZellulaereAutomatenPaktProzedur, build_zellulaere_automaten_pakt,
)
from kki.fitness_landschaft_manifest import (
    FitnessLandschaftManifest, FitnessLandschaftManifestGeltung, FitnessLandschaftManifestNorm,
    FitnessLandschaftManifestTyp, FitnessLandschaftManifestProzedur, build_fitness_landschaft_manifest,
)
from kki.adaptive_systeme_senat import (
    AdaptiveSystemeSenat, AdaptiveSystemeSenatGeltung, AdaptiveSystemeSenatNorm,
    AdaptiveSystemeSenatTyp, AdaptiveSystemeSenatProzedur, build_adaptive_systeme_senat,
)
from kki.synergetik_norm import (
    SynergetikNormSatz, SynergetikNormGeltung, SynergetikNormEintrag,
    SynergetikNormTyp, SynergetikNormProzedur, build_synergetik_norm,
)
from kki.kuenstliches_leben_charta import (
    KuenstlichesLebenCharta, KuenstlichesLebenChartaGeltung, KuenstlichesLebenChartaNorm,
    KuenstlichesLebenChartaTyp, KuenstlichesLebenChartaProzedur, build_kuenstliches_leben_charta,
)
from kki.komplexe_systeme_verfassung import (
    KomplexeSystemeVerfassung, KomplexeSystemeVerfassungsGeltung, KomplexeSystemeVerfassungsNorm,
    KomplexeSystemeVerfassungsTyp, KomplexeSystemeVerfassungsProzedur, build_komplexe_systeme_verfassung,
)
from kki import (
    KausalitaetsGeltung,
    KausalitaetsNorm,
    KausalitaetsProzedur,
    KausalitaetsRang,
    KausalitaetsRegister,
    build_kausalitaets_register,
    WirklichkeitsEbene,
    WirklichkeitsGeltung,
    WirklichkeitsKodex,
    WirklichkeitsNorm,
    WirklichkeitsProzedur,
    build_wirklichkeits_kodex,
    SeinsCharta,
    SeinsGeltung,
    SeinsNorm,
    SeinsProzedur,
    SeinsTyp,
    build_seins_charta,
    AxiomGeltung,
    AxiomProzedur,
    AxiomRang,
    UrsprungsAxiom,
    UrsprungsAxiomEintrag,
    build_ursprungs_axiom,
    TranszendenzEbene,
    TranszendenzGeltung,
    TranszendenzKodex,
    TranszendenzNorm,
    TranszendenzProzedur,
    build_transzendenz_kodex,
    ErkenntnisCharta,
    ErkenntnisGeltung,
    ErkenntnisNorm,
    ErkenntnisProzedur,
    ErkenntnisTyp,
    build_erkenntnis_charta,
    WeisheitsEbene,
    WeisheitsGeltung,
    WeisheitsNorm,
    WeisheitsNormEintrag,
    WeisheitsProzedur,
    build_weisheits_norm,
    GedaechtnisGeltung,
    GedaechtnisNorm,
    GedaechtnisProzedur,
    GedaechtnisRang,
    GedaechtnisSenat,
    build_gedaechtnis_senat,
    WissensGeltung,
    WissensGrad,
    WissensManifest,
    WissensNorm,
    WissensProzedur,
    build_wissens_manifest,
    KulturgutGeltung,
    KulturgutKodex,
    KulturgutNorm,
    KulturgutProzedur,
    KulturgutRang,
    build_kulturgut_kodex,
    ZivilisationsGeltung,
    ZivilisationsNorm,
    ZivilisationsPakt,
    ZivilisationsProzedur,
    ZivilisationsTyp,
    build_zivilisations_pakt,
    ErbeGeltung,
    ErbeKlasse,
    ErbeNorm,
    ErbeProzedur,
    ErbeRegister,
    build_erbe_register,
    SchoepfungsGeltung,
    SchoepfungsGrad,
    SchoepfungsNorm,
    SchoepfungsProzedur,
    SchoepfungsVertrag,
    build_schoepfungs_vertrag,
    UrsprungsCharta,
    UrsprungsGeltung,
    UrsprungsNorm,
    UrsprungsProzedur,
    UrsprungsTyp,
    build_ursprungs_charta,
    UniversalKodex,
    UniversalKodexGeltung,
    UniversalKodexKlasse,
    UniversalKodexNorm,
    UniversalKodexProzedur,
    build_universal_kodex,
    WeltgeistGeltung,
    WeltgeistProzedur,
    WeltgeistRang,
    WeltgeistSenat,
    WeltgeistSitz,
    build_weltgeist_senat,
    KosmosEbene,
    KosmosGeltung,
    KosmosNorm,
    KosmosNormEintrag,
    KosmosProzedur,
    build_kosmos_norm,
    DiplomatieCharta,
    DiplomatieGeltung,
    DiplomatieNorm,
    DiplomatieProzedur,
    DiplomatieRang,
    build_diplomatie_charta,
    VoelkerrechtsGeltung,
    VoelkerrechtsKlasse,
    VoelkerrechtsKodex,
    VoelkerrechtsNorm,
    VoelkerrechtsProzedur,
    build_voelkerrechts_kodex,
    WeltordnungsEbene,
    WeltordnungsGeltung,
    WeltordnungsNorm,
    WeltordnungsPrinzip,
    WeltordnungsProzedur,
    build_weltordnungs_prinzip,
    DoctrineClause,
    DoctrinePrinciple,
    DoctrineScope,
    DoctrineStatus,
    CompassStatus,
    CharterStatus,
    DiplomacyChannel,
    DiplomacyPath,
    DiplomacyPosture,
    DiplomacyStatus,
    ExecutionCabinet,
    LeitsternDoctrine,
    LeitsternCodex,
    MissionsCollegium,
    PriorityConclave,
    RegisterRetention,
    RegisterTier,
    CourseContract,
    VetoSluice,
    DecisionArchive,
    DelegationMatrix,
    DirectiveConsensus,
    GuidelineCompass,
    GuidelinePrinciple,
    GuidelineVector,
    InterventionCharter,
    InterventionClause,
    InterventionRight,
    MandateMemoryRecord,
    MandateMemoryStatus,
    MandateMemoryStore,
    NavigationConstraint,
    ProgramSenate,
    ReleaseThreshold,
    SenateBalanceStatus,
    SenatePriority,
    SenateResolution,
    SenateSeat,
    StopCondition,
    CockpitEntry,
    CockpitStatus,
    ConstitutionArticle,
    ConstitutionPrinciple,
    ConstitutionalAuthority,
    ControlArtifact,
    CoreState,
    DelegationGrant,
    DeliveryGuarantee,
    DeliveryMode,
    DriftMonitor,
    DriftObservation,
    DriftSeverity,
    DispatchLane,
    DispatchTriageMode,
    EscalationDirective,
    EscalationPath,
    EscalationPlan,
    EscalationRoute,
    EscalationRoutePath,
    EscalationRouter,
    EvidenceLedger,
    EvidenceLedgerEntry,
    EvidenceLedgerSource,
    ExecutiveOrder,
    ExecutiveOrderMode,
    ExecutiveWatchStatus,
    ExecutiveWatchtower,
    ExceptionCase,
    ExceptionKind,
    ExceptionRegister,
    ExceptionSeverity,
    FederationAlignmentStatus,
    FederationCell,
    FederationCoordination,
    FederationDomain,
    FederationHandoff,
    FederationHandoffPriority,
    EvidenceRecord,
    EventEnvelope,
    GateDecision,
    GateReadiness,
    GateState,
    GateOutcome,
    Guardrail,
    GuardrailDomain,
    GuardrailPolicyMode,
    GuardrailPortfolio,
    GovernanceAgenda,
    GovernanceAgendaItem,
    GovernanceAgendaStatus,
    HandoffMode,
    HumanDecision,
    HumanLoopGovernance,
    IdentityKind,
    ImprovementExecutionMode,
    ImprovementOrchestrator,
    ImprovementPriority,
    ImprovementWave,
    IncidentCause,
    IncidentReport,
    IncidentSeverity,
    IntegratedOperationsRun,
    IntegratedSmokeBuild,
    InterventionFallback,
    InterventionMode,
    InterventionSimulation,
    InterventionSimulationStatus,
    InterventionSimulator,
    LearningPatternType,
    LearningRecord,
    LearningRegister,
    LoadedControlPlane,
    MissionPolicy,
    MissionProfile,
    MissionScenario,
    MandateCard,
    MandateCardDeck,
    MandateExecutionScope,
    MandateReviewCadence,
    MessageEnvelope,
    MessageKind,
    ModuleBoundaryName,
    OperationalPressure,
    OperationsRunLedger,
    OperationsCockpit,
    OperationsSteward,
    OperationsStewardStatus,
    OutcomeLedger,
    OutcomeRecord,
    OutcomeStatus,
    OperatingConstitution,
    OperationsWave,
    OperatingMode,
    OperationsIncident,
    OrchestrationStatus,
    PlaybookCatalog,
    PlaybookEntry,
    PlaybookReadiness,
    PlaybookType,
    PortfolioAction,
    PortfolioConcentration,
    PortfolioExposure,
    PortfolioOperatingSpread,
    PortfolioOptimizer,
    PortfolioPriority,
    PortfolioRadar,
    PortfolioRadarEntry,
    PortfolioRecommendation,
    PolicyTuneAction,
    PolicyTuneEntry,
    PolicyTuner,
    ProgramController,
    ProgramControllerStatus,
    ProgramDirective,
    ProgramTrack,
    ProgramTrackType,
    PersistenceRecord,
    PreviewMode,
    ShadowCoordination,
    ShadowCoordinationMode,
    StewardDirective,
    StewardDirectiveType,
    StewardWorkboard,
    StrategyCouncil,
    StrategyCouncilStatus,
    StrategyEscalationMandate,
    StrategyLane,
    StrategyMandate,
    StrategyPriority,
    ProtocolContext,
    ReadinessCadence,
    ReadinessCadenceEntry,
    ReadinessCadenceStatus,
    ReadinessCadenceTrigger,
    ReadinessCadenceWindow,
    RecoveryCheckpoint,
    RecoveryDrill,
    RecoveryDrillStatus,
    RecoveryDrillSuite,
    ReadinessFinding,
    ReadinessFindingSeverity,
    ReadinessReview,
    RemediationCampaign,
    RemediationCampaignStage,
    RemediationCampaignStageType,
    RemediationCampaignStatus,
    RecoveryDisposition,
    RecoveryMode,
    RecoveryOrchestration,
    RecoveryOutcome,
    ReleaseCampaign,
    ReleaseCampaignStage,
    ReleaseCampaignStageType,
    ReleaseCampaignStatus,
    ReviewActionItem,
    ReviewActionPlan,
    ReviewActionPriority,
    ReviewActionType,
    RiskImpact,
    RiskLikelihood,
    RiskMitigationStatus,
    RiskRecord,
    RiskRegister,
    ReplayMode,
    RoleName,
    RolloutPhase,
    RolloutState,
    RollbackDirective,
    RunLedgerEntry,
    RuntimeScorecard,
    RuntimeScorecardEntry,
    RuntimeStage,
    RuntimeThresholds,
    ScenarioReplayItem,
    ScenarioReplayResult,
    ScenarioReplaySuite,
    ScenarioChancery,
    ScenarioOfficeMode,
    ScenarioOfficeStatus,
    ScenarioOption,
    ShadowPreview,
    TelemetryAlert,
    TelemetrySignal,
    TelemetrySnapshot,
    TransferEnvelope,
    TrustLevel,
    ValidationStep,
    WaveBudgetPolicy,
    WorkboardItem,
    WorkboardLane,
    WorkboardQueue,
    WorkboardStatus,
    WorkPriority,
    WorkStatus,
    authorize_action,
    authorize_artifact,
    advance_orchestration_state,
    advance_rollout_state,
    advance_work_unit,
    audit_entry_for_artifact,
    audit_entry_for_message,
    benchmark_case_matrix,
    build_autonomy_governor,
    build_capacity_planner,
    build_continuous_readiness_cycle,
    build_convergence_simulator,
    build_course_corrector,
    build_decision_archive,
    build_delegation_matrix,
    build_execution_cabinet,
    build_consensus_diplomacy,
    build_leitstern_doctrine,
    build_missions_collegium,
    build_priority_conclave,
    build_course_contract,
    build_leitstern_codex,
    build_kodex_register,
    build_satzungs_rat,
    build_mandats_konvent,
    build_veto_sluice,
    build_directive_consensus,
    build_dispatch_plan,
    build_drift_monitor,
    build_escalation_router,
    build_evidence_ledger,
    build_executive_watchtower,
    build_exception_register,
    build_federation_coordination,
    build_guideline_compass,
    build_governance_agenda,
    build_guardrail_portfolio,
    build_improvement_orchestrator,
    build_intervention_charter,
    build_intervention_simulator,
    build_learning_register,
    build_mandate_card_deck,
    build_mandate_memory_store,
    build_operations_cockpit,
    build_operations_steward,
    build_operating_constitution,
    build_outcome_ledger,
    build_playbook_catalog,
    build_portfolio_optimizer,
    build_portfolio_radar,
    build_policy_tuner,
    build_program_controller,
    build_program_senate,
    build_readiness_cadence,
    build_remediation_campaign,
    build_readiness_review,
    build_recovery_drill_suite,
    build_release_campaign,
    build_review_action_plan,
    build_risk_register,
    build_scenario_replay,
    build_scenario_chancery,
    build_runtime_scorecard,
    build_steward_workboard,
    build_strategy_council,
    build_telemetry_snapshot,
    claim_for_work_unit,
    coordinate_escalations,
    command_message,
    coordinate_shadow_work,
    correlate_operation,
    core_state_for_runtime,
    detect_incidents,
    evaluate_dry_run,
    evaluate_gate,
    event_message,
    evidence_message,
    govern_recovery_orchestration,
    load_control_plane,
    ledger_for_wave,
    module_boundaries,
    module_dependency_graph,
    mission_profile_catalog,
    mission_profile_for_name,
    orchestration_state_for_runtime,
    orchestrate_recovery_for_rollout,
    protocol_context,
    recovery_checkpoint_for_state,
    recovery_outcome,
    rollback_directive_for_checkpoint,
    rollout_state_for_shadow,
    run_benchmark_harness,
    run_integrated_smoke_build,
    run_integrated_operations,
    run_operations_wave,
    runtime_dna_for_profile,
    runtime_dna_from_env,
    handoff_for_work_unit,
    operation_alerts,
    open_change_window,
    shadow_event,
    shadow_preview_for_command,
    shadow_snapshot,
    telemetry_alert,
    telemetry_signal_from_event,
    transfer_message,
    transfer_envelope_for_state,
    work_unit_for_state,
)

REPO_ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable


class SmokeTests(unittest.TestCase):
    def run_script(
        self,
        script_name: str,
        output_dir: Path,
        seed: int = 42,
        extra_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(
            {
                "KKI_SEED": str(seed),
                "KKI_TEST_MODE": "1",
                "KKI_TEST_ROUNDS": "6",
                "KKI_TEST_INTERACTIONS": "8",
                "KKI_TEST_INVASION_ROUND": "3",
                "KKI_OUTPUT_DIR": str(output_dir),
                "MPLBACKEND": "Agg",
                "PYTHONUNBUFFERED": "1",
            }
        )
        if extra_env:
            env.update(extra_env)
        result = subprocess.run(
            [PYTHON, script_name],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        return result

    def assert_successful_run(self, result: subprocess.CompletedProcess[str]) -> None:
        if result.returncode != 0:
            self.fail(
                f"Skript schlug fehl ({result.returncode}).\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_runtime_dna_foundation_profile(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        exported = dna.to_dict()

        self.assertEqual(exported["identity"]["stage"], "shadow")
        self.assertIn("telemetry", exported["enabled_hooks"])
        self.assertIn("audit-before-cutover", exported["invariants"])
        self.assertGreater(exported["thresholds"]["resource_budget"], exported["thresholds"]["recovery_reserve"])

    def test_runtime_dna_env_overrides(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "KKI_RUNTIME_PROFILE": "pilot-runtime-dna",
                "KKI_RUNTIME_STAGE": "pilot",
                "KKI_RUNTIME_RESOURCE_BUDGET": "0.81",
                "KKI_RUNTIME_RECOVERY_RESERVE": "0.21",
                "KKI_RUNTIME_ENABLE_SHADOW": "false",
                "KKI_RUNTIME_OWNER": "copilot",
            },
            clear=False,
        ):
            dna = runtime_dna_from_env()

        self.assertEqual(dna.identity.profile, "pilot-runtime-dna")
        self.assertEqual(dna.identity.stage, RuntimeStage.PILOT)
        self.assertAlmostEqual(dna.thresholds.resource_budget, 0.81)
        self.assertAlmostEqual(dna.thresholds.recovery_reserve, 0.21)
        self.assertFalse(dna.hooks.shadow)
        self.assertEqual(dna.metadata["owner"], "copilot")

    def test_runtime_thresholds_reject_invalid_reserve(self) -> None:
        with self.assertRaises(ValueError):
            RuntimeThresholds(resource_budget=0.2, recovery_reserve=0.2)

    def test_kki_module_boundaries_are_importable(self) -> None:
        boundaries = module_boundaries()

        self.assertEqual(boundaries[0].name, ModuleBoundaryName.ORCHESTRATION)
        self.assertEqual(boundaries[-1].name, ModuleBoundaryName.GOVERNANCE)
        self.assertTrue(all(boundary.package.startswith("kki.") for boundary in boundaries))

    def test_kki_module_dependency_graph_is_stable(self) -> None:
        graph = module_dependency_graph()

        self.assertEqual(graph["orchestration"], ())
        self.assertEqual(graph["telemetry"], ("orchestration",))
        self.assertEqual(graph["shadow"], ("telemetry", "security"))
        self.assertEqual(graph["governance"], ("security", "rollout", "recovery"))

    def test_kki_core_state_snapshot_is_canonical(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = core_state_for_runtime(
            dna,
            module=ModuleBoundaryName.ORCHESTRATION,
            status="ready",
            budget=0.61,
            labels={"owner": "build-phase"},
        )

        self.assertIsInstance(state, CoreState)
        exported = state.to_dict()
        self.assertEqual(exported["module_boundary"], "orchestration")
        self.assertEqual(exported["runtime_stage"], "shadow")
        self.assertEqual(exported["labels"]["owner"], "build-phase")

    def test_kki_transfer_envelope_wraps_state(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = core_state_for_runtime(dna, module="orchestration", status="promoting", budget=0.7)
        envelope = transfer_envelope_for_state(
            state,
            target_boundary="rollout",
            correlation_id="corr-123",
            causation_id="cause-1",
            sequence=2,
        )

        self.assertIsInstance(envelope, TransferEnvelope)
        exported = envelope.to_dict()
        self.assertEqual(exported["target_boundary"], "rollout")
        self.assertEqual(exported["payload_type"], "core-state")
        self.assertEqual(exported["payload"]["status"], "promoting")
        self.assertEqual(exported["sequence"], 2)

    def test_kki_persistence_record_rejects_invalid_retention(self) -> None:
        with self.assertRaises(ValueError):
            PersistenceRecord(
                record_type="snapshot",
                boundary=ModuleBoundaryName.RECOVERY,
                schema_version="1.0",
                retention_class="permanent",
                payload={"restart": True},
            )

    def test_kki_evidence_record_is_exportable(self) -> None:
        evidence = EvidenceRecord(
            evidence_type="approval",
            subject="cutover-gate",
            correlation_id="corr-9",
            audit_ref="audit-42",
            commitment_ref="commit-7",
            payload={"decision": "approved"},
        )

        exported = evidence.to_dict()
        self.assertEqual(exported["audit_ref"], "audit-42")
        self.assertEqual(exported["commitment_ref"], "commit-7")
        self.assertEqual(exported["payload"]["decision"], "approved")

    def test_kki_orchestration_state_tracks_health_markers(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-131",
            status=OrchestrationStatus.ACTIVE,
            budget_available=0.78,
            budget_reserved=0.22,
            pressure=OperationalPressure(0.44, 0.41, 0.28, 0.18),
            open_risks=("drift-watch",),
            labels={"wave": "131"},
        )

        exported = state.to_dict()
        self.assertEqual(exported["status"], "active")
        self.assertEqual(exported["health_status"], "healthy")
        self.assertIn("pressure:elevated", exported["health_markers"])
        self.assertEqual(exported["dispatch_budget"], 0.56)
        self.assertTrue(state.recovery_ready)

    def test_kki_orchestration_state_detects_blocked_recovery(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-131",
            status=OrchestrationStatus.DEGRADED,
            budget_available=0.72,
            budget_reserved=0.14,
            pressure=OperationalPressure(0.78, 0.72, 0.67, 0.58),
            gates=GateReadiness(recovery=GateState.BLOCKED, blockers=("reserve breach",)),
            open_risks=("drift", "queue-backlog", "operator-gate"),
        )

        self.assertFalse(state.recovery_ready)
        self.assertEqual(state.health_status(), "gated")
        self.assertIn("gates:blocked", state.health_markers())
        self.assertIn("risks-hot", state.health_markers())

    def test_kki_orchestration_state_validates_transitions(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        staged = orchestration_state_for_runtime(dna, mission_ref="mission-131")
        active = advance_orchestration_state(
            staged,
            status=OrchestrationStatus.ACTIVE,
            pressure=OperationalPressure(0.31, 0.22, 0.18, 0.12),
            labels={"handoff": "accepted"},
        )

        self.assertEqual(active.status, OrchestrationStatus.ACTIVE)
        self.assertEqual(active.labels["handoff"], "accepted")
        self.assertEqual(active.health_status(), "healthy")

        with self.assertRaises(ValueError):
            advance_orchestration_state(active, status=OrchestrationStatus.BOOTSTRAPPING)

    def test_kki_orchestration_state_exports_core_state(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-131",
            status=OrchestrationStatus.THROTTLED,
            budget_available=0.75,
            budget_reserved=0.19,
            pressure=OperationalPressure(0.64, 0.57, 0.33, 0.21),
        )
        core_state = state.to_core_state()
        exported = core_state.to_dict()

        self.assertEqual(exported["module_boundary"], "orchestration")
        self.assertEqual(exported["status"], "throttled")
        self.assertEqual(exported["labels"]["pressure_level"], "elevated")
        self.assertEqual(exported["labels"]["health_status"], "degraded")

    def test_kki_work_unit_is_built_from_orchestration_state(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-132",
            status=OrchestrationStatus.ACTIVE,
            budget_available=0.79,
            budget_reserved=0.21,
            pressure=OperationalPressure(0.54, 0.48, 0.29, 0.22),
        )
        work_unit = work_unit_for_state(
            state,
            title="shadow preview dispatch",
            boundary="shadow",
            correlation_id="corr-wu",
            priority=WorkPriority.HIGH,
            required_capabilities=("preview", "drift-check"),
        )

        exported = work_unit.to_dict()
        self.assertEqual(exported["boundary"], "shadow")
        self.assertEqual(exported["priority"], "high")
        self.assertEqual(exported["status"], "planned")
        self.assertTrue(exported["ready_for_claim"])
        self.assertEqual(exported["labels"]["pressure_level"], "elevated")

    def test_kki_claim_uses_handoff_target_boundary(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(dna, mission_ref="mission-132")
        work_unit = work_unit_for_state(
            state,
            title="rollout evaluation",
            boundary="shadow",
            correlation_id="corr-claim",
        )
        handoff = handoff_for_work_unit(
            work_unit,
            target_boundary="rollout",
            reason="promotion review path",
            mode=HandoffMode.SHADOW,
            retry_budget=2,
        )
        transferred = advance_work_unit(
            work_unit,
            status=WorkStatus.HANDED_OFF,
            handoff_ref=handoff.handoff_id,
            labels={"handoff_mode": handoff.mode.value},
        )
        claim = claim_for_work_unit(
            transferred,
            owner_ref="rollout-planner",
            boundary="rollout",
            handoff=handoff,
        )

        self.assertEqual(claim.status, ClaimStatus.ACTIVE)
        self.assertEqual(claim.boundary, ModuleBoundaryName.ROLLOUT)
        self.assertEqual(claim.handoff_ref, handoff.handoff_id)

    def test_kki_work_unit_transition_rejects_invalid_reset(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = orchestration_state_for_runtime(dna, mission_ref="mission-132")
        work_unit = work_unit_for_state(
            state,
            title="telemetry stitching",
            boundary="telemetry",
            correlation_id="corr-transition",
        )
        claimed = advance_work_unit(work_unit, status=WorkStatus.CLAIMED)
        active = advance_work_unit(claimed, status=WorkStatus.IN_PROGRESS, attempt=1)

        self.assertEqual(active.status, WorkStatus.IN_PROGRESS)
        self.assertEqual(active.attempt, 1)

        with self.assertRaises(ValueError):
            advance_work_unit(active, status=WorkStatus.PLANNED)

    def test_kki_handoff_contract_preserves_retry_metadata(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-132",
            status=OrchestrationStatus.THROTTLED,
            pressure=OperationalPressure(0.55, 0.62, 0.31, 0.47),
        )
        work_unit = work_unit_for_state(
            state,
            title="recovery staging",
            boundary="shadow",
            correlation_id="corr-handoff",
            priority=WorkPriority.CRITICAL,
            max_retries=3,
        )
        handoff = handoff_for_work_unit(
            work_unit,
            target_boundary="recovery",
            reason="critical drift escalation",
            mode=HandoffMode.RECOVERY,
            causation_id="shadow-drift",
        )

        exported = handoff.to_dict()
        self.assertEqual(exported["target_boundary"], "recovery")
        self.assertEqual(exported["retry_budget"], 3)
        self.assertEqual(exported["mode"], "recovery")
        self.assertEqual(exported["causation_id"], "shadow-drift")

    def test_kki_dispatch_plan_admits_high_priority_within_budget(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-133",
            status=OrchestrationStatus.ACTIVE,
            budget_available=0.8,
            budget_reserved=0.22,
            pressure=OperationalPressure(0.41, 0.58, 0.24, 0.19),
        )
        work_units = (
            work_unit_for_state(
                state,
                title="shadow verify",
                boundary="shadow",
                correlation_id="dispatch-1",
                priority=WorkPriority.HIGH,
                budget_share=0.18,
            ),
            work_unit_for_state(
                state,
                title="telemetry aggregate",
                boundary="telemetry",
                correlation_id="dispatch-2",
                priority=WorkPriority.NORMAL,
                budget_share=0.16,
            ),
            work_unit_for_state(
                state,
                title="recovery hold",
                boundary="recovery",
                correlation_id="dispatch-3",
                priority=WorkPriority.CRITICAL,
                budget_share=0.2,
            ),
        )

        plan = build_dispatch_plan(
            state,
            work_units,
            available_roles=(RoleName.EXECUTOR, RoleName.SUPERVISOR),
            max_parallel=2,
        )

        self.assertEqual(plan.triage_mode, DispatchTriageMode.BACKLOG)
        self.assertEqual(len(plan.admitted_unit_ids), 2)
        self.assertIn(work_units[2].unit_id, plan.admitted_unit_ids)
        self.assertLessEqual(plan.consumed_budget, plan.effective_budget)

    def test_kki_dispatch_plan_holds_work_when_dispatch_guarded(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-133",
            status=OrchestrationStatus.THROTTLED,
            gates=GateReadiness(dispatch=GateState.GUARDED),
            pressure=OperationalPressure(0.52, 0.44, 0.2, 0.18),
        )
        normal_work = work_unit_for_state(
            state,
            title="normal rollout sync",
            boundary="rollout",
            correlation_id="dispatch-guarded",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
        )

        plan = build_dispatch_plan(state, (normal_work,))

        self.assertEqual(plan.assignments[0].lane, DispatchLane.HOLD)
        self.assertIn(normal_work.unit_id, plan.held_unit_ids)

    def test_kki_dispatch_plan_blocks_when_gate_blocked(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-133",
            gates=GateReadiness(dispatch=GateState.BLOCKED, blockers=("operator stop",)),
        )
        work_unit = work_unit_for_state(
            state,
            title="shadow replay",
            boundary="shadow",
            correlation_id="dispatch-blocked",
            priority=WorkPriority.HIGH,
        )

        plan = build_dispatch_plan(state, (work_unit,))

        self.assertEqual(plan.assignments[0].lane, DispatchLane.BLOCK)
        self.assertEqual(plan.assignments[0].rationale, "dispatch gate is blocked")

    def test_kki_dispatch_plan_protects_reserve_gap(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-133",
            status=OrchestrationStatus.DEGRADED,
            budget_available=0.76,
            budget_reserved=0.12,
            pressure=OperationalPressure(0.67, 0.48, 0.41, 0.54),
        )
        work_units = (
            work_unit_for_state(
                state,
                title="recovery checkpoint sync",
                boundary="recovery",
                correlation_id="dispatch-gap-1",
                priority=WorkPriority.CRITICAL,
                budget_share=0.22,
            ),
            work_unit_for_state(
                state,
                title="shadow backlog cleanup",
                boundary="shadow",
                correlation_id="dispatch-gap-2",
                priority=WorkPriority.NORMAL,
                budget_share=0.18,
                recovery_weight=0.18,
            ),
        )

        plan = build_dispatch_plan(state, work_units, max_parallel=2)

        self.assertEqual(plan.triage_mode, DispatchTriageMode.RECOVERY_PRIORITY)
        self.assertEqual(plan.assignments[0].lane, DispatchLane.ADMIT)
        self.assertEqual(plan.assignments[1].lane, DispatchLane.HOLD)
        self.assertLess(plan.effective_budget, plan.dispatch_budget)

    def test_kki_gate_decision_approves_admitted_rollout(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        identity = AuthorizationIdentity(
            slug="gatekeeper-rollout",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("rollout", "governance"),
        )
        state = orchestration_state_for_runtime(runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT), mission_ref="mission-134")
        work_unit = work_unit_for_state(
            state,
            title="rollout promotion",
            boundary="rollout",
            correlation_id="gate-rollout",
            priority=WorkPriority.HIGH,
            budget_share=0.15,
        )
        dispatch_plan = build_dispatch_plan(state, (work_unit,), available_roles=(RoleName.EXECUTOR,))
        message = command_message(
            name="approve-promotion",
            source_boundary="governance",
            target_boundary="rollout",
            correlation_id="gate-rollout",
            payload={"target": "pilot-wave"},
        )

        decision = evaluate_gate(
            identity,
            boundary="rollout",
            control_plane=control_plane,
            message=message,
            dispatch_assignment=dispatch_plan.assignments[0],
            evidence_ref="audit-rollout-policy",
        )

        self.assertIsInstance(decision, GateDecision)
        self.assertEqual(decision.outcome, GateOutcome.GO)
        self.assertTrue(decision.evidence_required)

    def test_kki_gate_decision_holds_dispatch_hold_assignment(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict"},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow",),
        )
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-134",
            status=OrchestrationStatus.THROTTLED,
            gates=GateReadiness(dispatch=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="shadow preview",
            boundary="shadow",
            correlation_id="gate-hold",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
        )
        dispatch_plan = build_dispatch_plan(state, (work_unit,))
        message = command_message(
            name="run-shadow-preview",
            source_boundary="orchestration",
            target_boundary="shadow",
            correlation_id="gate-hold",
            payload={"preview": True},
        )

        decision = evaluate_gate(
            identity,
            boundary="shadow",
            control_plane=control_plane,
            message=message,
            dispatch_assignment=dispatch_plan.assignments[0],
        )

        self.assertEqual(decision.outcome, GateOutcome.HOLD)
        self.assertIn("dispatch planner requested hold", decision.reason)

    def test_kki_gate_decision_blocks_on_scope_denial(self) -> None:
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.SHADOW, boundary="recovery")
        identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow",),
        )
        message = command_message(
            name="start-recovery",
            source_boundary="shadow",
            target_boundary="recovery",
            correlation_id="gate-block",
            payload={"rollback": True},
        )

        decision = evaluate_gate(
            identity,
            boundary="recovery",
            control_plane=control_plane,
            message=message,
            operating_mode=OperatingMode.RECOVERY,
            evidence_ref="audit-recovery",
        )

        self.assertEqual(decision.outcome, GateOutcome.BLOCK)
        self.assertIn("identity scope", decision.blockers[0])

    def test_kki_gate_decision_escalates_emergency_override(self) -> None:
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        identity = AuthorizationIdentity(
            slug="supervisor-emergency",
            kind=IdentityKind.SUPERVISOR,
            role=RoleName.SUPERVISOR,
            trust_level=TrustLevel.EMERGENCY,
            boundary_scope=("recovery", "security"),
        )
        message = command_message(
            name="emergency-recovery",
            source_boundary="governance",
            target_boundary="recovery",
            correlation_id="gate-escalate",
            payload={"override": "restart"},
        )

        decision = evaluate_gate(
            identity,
            boundary="recovery",
            control_plane=control_plane,
            message=message,
            operating_mode=OperatingMode.EMERGENCY,
            evidence_ref="audit-override",
        )

        self.assertEqual(decision.outcome, GateOutcome.ESCALATE)
        self.assertTrue(decision.evidence_required)
        self.assertTrue(decision.escalation_required)

    def test_kki_correlate_operation_builds_snapshot(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict"},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-135",
        )
        work_unit = work_unit_for_state(
            state,
            title="shadow correlate",
            boundary="shadow",
            correlation_id="corr-135",
            priority=WorkPriority.HIGH,
            budget_share=0.15,
        )
        dispatch_plan = build_dispatch_plan(state, (work_unit,), available_roles=(RoleName.EXECUTOR,))
        identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow",),
        )
        message = command_message(
            name="run-shadow-preview",
            source_boundary="orchestration",
            target_boundary="shadow",
            correlation_id="corr-135",
            payload={"preview": True},
        )
        gate = evaluate_gate(
            identity,
            boundary="shadow",
            control_plane=control_plane,
            message=message,
            dispatch_assignment=dispatch_plan.assignments[0],
        )

        correlated = correlate_operation(
            control_plane=control_plane,
            message=message,
            dispatch_assignment=dispatch_plan.assignments[0],
            gate_decision=gate,
        )

        self.assertIsInstance(correlated, CorrelatedOperation)
        self.assertEqual(correlated.snapshot.highest_severity(), "info")
        self.assertEqual(len(correlated.signals), 3)
        self.assertIn("shadow-policy", correlated.snapshot.active_controls)

    def test_kki_operation_alerts_raise_for_blocked_gate(self) -> None:
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.SHADOW, boundary="recovery")
        identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow",),
        )
        message = command_message(
            name="start-recovery",
            source_boundary="shadow",
            target_boundary="recovery",
            correlation_id="corr-135-block",
            payload={"rollback": True},
        )
        gate = evaluate_gate(
            identity,
            boundary="recovery",
            control_plane=control_plane,
            message=message,
            operating_mode=OperatingMode.RECOVERY,
            evidence_ref="audit-recovery",
        )

        alerts = operation_alerts(message=message, gate_decision=gate)

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].severity, "critical")

    def test_kki_correlate_operation_keeps_dispatch_audit(self) -> None:
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-135",
            status=OrchestrationStatus.THROTTLED,
            gates=GateReadiness(dispatch=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="rollout hold",
            boundary="rollout",
            correlation_id="corr-135-hold",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
        )
        dispatch_plan = build_dispatch_plan(state, (work_unit,))
        message = command_message(
            name="approve-rollout",
            source_boundary="governance",
            target_boundary="rollout",
            correlation_id="corr-135-hold",
            payload={"target": "wave"},
        )

        correlated = correlate_operation(
            control_plane=control_plane,
            message=message,
            dispatch_assignment=dispatch_plan.assignments[0],
        )

        entry_types = [entry.entry_type for entry in correlated.audit_entries]
        self.assertIn("dispatch-assignment", entry_types)
        self.assertEqual(correlated.alerts[0].severity, "warning")

    def test_kki_correlate_operation_gate_alerts_raise_snapshot_severity(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-135",
            status=OrchestrationStatus.THROTTLED,
            gates=GateReadiness(dispatch=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="rollout pending",
            boundary="rollout",
            correlation_id="corr-135-rollout",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
        )
        dispatch_plan = build_dispatch_plan(state, (work_unit,))
        identity = AuthorizationIdentity(
            slug="gatekeeper-rollout",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("rollout", "governance"),
        )
        message = command_message(
            name="approve-promotion",
            source_boundary="governance",
            target_boundary="rollout",
            correlation_id="corr-135-rollout",
            payload={"target": "pilot-wave"},
        )
        gate = evaluate_gate(
            identity,
            boundary="rollout",
            control_plane=control_plane,
            message=message,
            dispatch_assignment=dispatch_plan.assignments[0],
            evidence_ref="audit-rollout-policy",
        )

        correlated = correlate_operation(
            control_plane=control_plane,
            message=message,
            dispatch_assignment=dispatch_plan.assignments[0],
            gate_decision=gate,
        )

        self.assertEqual(gate.outcome, GateOutcome.HOLD)
        self.assertEqual(correlated.snapshot.highest_severity(), "warning")

    def test_kki_shadow_coordination_builds_release_ready_preview(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-136",
        )
        work_unit = work_unit_for_state(
            state,
            title="shadow preview",
            boundary="rollout",
            correlation_id="corr-136-preview",
            priority=WorkPriority.HIGH,
            budget_share=0.15,
        )
        identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )

        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=control_plane,
            identity=identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.15,
        )

        self.assertIsInstance(coordination, ShadowCoordination)
        self.assertEqual(coordination.mode, ShadowCoordinationMode.PREVIEW)
        self.assertTrue(coordination.release_ready)
        self.assertEqual(coordination.release_signal.status, "release-ready")
        self.assertEqual(coordination.correlation.snapshot.highest_severity(), "info")

    def test_kki_shadow_coordination_switches_to_parallel_mode(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-136",
            gates=GateReadiness(shadow=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="parallel validation",
            boundary="rollout",
            correlation_id="corr-136-parallel",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
        )
        identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )

        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=control_plane,
            identity=identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.14,
        )

        self.assertEqual(coordination.mode, ShadowCoordinationMode.PARALLEL)
        self.assertFalse(coordination.release_ready)
        self.assertEqual(coordination.release_signal.status, "parallel-required")

    def test_kki_shadow_coordination_clears_replay_for_handoff_work(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-136",
        )
        work_unit = work_unit_for_state(
            state,
            title="replay validation",
            boundary="rollout",
            correlation_id="corr-136-replay",
            priority=WorkPriority.HIGH,
            budget_share=0.12,
        )
        replay_unit = advance_work_unit(
            work_unit,
            status=WorkStatus.HANDED_OFF,
            attempt=1,
            handoff_ref="handoff-replay",
        )
        identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )

        coordination = coordinate_shadow_work(
            state,
            replay_unit,
            control_plane=control_plane,
            identity=identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.12,
        )

        self.assertEqual(coordination.mode, ShadowCoordinationMode.REPLAY)
        self.assertTrue(coordination.release_ready)
        self.assertEqual(coordination.release_signal.status, "replay-cleared")
        self.assertEqual(coordination.preview.mode, PreviewMode.DRY_RUN)

    def test_kki_shadow_coordination_blocks_release_when_gate_denies(self) -> None:
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-136",
        )
        work_unit = work_unit_for_state(
            state,
            title="blocked shadow run",
            boundary="rollout",
            correlation_id="corr-136-blocked",
            priority=WorkPriority.HIGH,
            budget_share=0.14,
        )
        identity = AuthorizationIdentity(
            slug="observer-shadow",
            kind=IdentityKind.OPERATOR,
            role=RoleName.OBSERVER,
            trust_level=TrustLevel.RESTRICTED,
            boundary_scope=("shadow",),
        )

        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=control_plane,
            identity=identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.14,
        )

        self.assertFalse(coordination.release_ready)
        self.assertEqual(coordination.release_signal.status, "blocked")
        self.assertEqual(coordination.release_signal.severity, "critical")
        self.assertEqual(coordination.gate_decision.outcome, GateOutcome.BLOCK)

    def test_kki_rollout_state_promotes_release_ready_shadow(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        shadow_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-137",
        )
        work_unit = work_unit_for_state(
            state,
            title="promote release",
            boundary="rollout",
            correlation_id="corr-137-promote",
            priority=WorkPriority.HIGH,
            budget_share=0.15,
        )
        shadow_identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )
        rollout_identity = AuthorizationIdentity(
            slug="gatekeeper-rollout",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("rollout", "governance"),
        )
        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=shadow_plane,
            identity=shadow_identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.15,
        )

        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=rollout_identity,
            evidence_ref="audit-rollout-policy",
        )

        self.assertIsInstance(rollout_state, RolloutState)
        self.assertEqual(rollout_state.phase, RolloutPhase.PROMOTING)
        self.assertTrue(rollout_state.promotion_ready)
        self.assertEqual(rollout_state.promotion_signal.status, "promoting")
        self.assertEqual(rollout_state.to_core_state().module_boundary, ModuleBoundaryName.ROLLOUT)

    def test_kki_rollout_state_stages_parallel_shadow_release(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        shadow_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-137",
            gates=GateReadiness(shadow=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="parallel rollout staging",
            boundary="rollout",
            correlation_id="corr-137-stage",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
        )
        shadow_identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )
        rollout_identity = AuthorizationIdentity(
            slug="gatekeeper-rollout",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("rollout", "governance"),
        )
        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=shadow_plane,
            identity=shadow_identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.14,
        )

        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=rollout_identity,
            evidence_ref="audit-rollout-policy",
        )

        self.assertEqual(coordination.release_signal.status, "parallel-required")
        self.assertEqual(rollout_state.phase, RolloutPhase.STAGED)
        self.assertFalse(rollout_state.promotion_ready)

    def test_kki_rollout_state_moves_replay_release_into_canary(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        shadow_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-137",
        )
        work_unit = work_unit_for_state(
            state,
            title="replay release",
            boundary="rollout",
            correlation_id="corr-137-canary",
            priority=WorkPriority.HIGH,
            budget_share=0.12,
        )
        replay_unit = advance_work_unit(
            work_unit,
            status=WorkStatus.HANDED_OFF,
            attempt=1,
            handoff_ref="handoff-rollout-replay",
        )
        shadow_identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )
        rollout_identity = AuthorizationIdentity(
            slug="gatekeeper-rollout",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("rollout", "governance"),
        )
        coordination = coordinate_shadow_work(
            state,
            replay_unit,
            control_plane=shadow_plane,
            identity=shadow_identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.12,
        )

        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=rollout_identity,
            evidence_ref="audit-rollout-policy",
        )
        active_state = advance_rollout_state(rollout_state, phase=RolloutPhase.ACTIVE)

        self.assertEqual(rollout_state.phase, RolloutPhase.CANARY)
        self.assertEqual(active_state.phase, RolloutPhase.ACTIVE)
        self.assertTrue(active_state.promotion_ready)

    def test_kki_rollout_state_marks_blocked_promotion_as_rollback_ready(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
        )
        shadow_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-137",
        )
        work_unit = work_unit_for_state(
            state,
            title="blocked promotion",
            boundary="rollout",
            correlation_id="corr-137-blocked",
            priority=WorkPriority.HIGH,
            budget_share=0.15,
        )
        shadow_identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )
        denied_rollout_identity = AuthorizationIdentity(
            slug="observer-rollout",
            kind=IdentityKind.OPERATOR,
            role=RoleName.OBSERVER,
            trust_level=TrustLevel.RESTRICTED,
            boundary_scope=("rollout",),
        )
        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=shadow_plane,
            identity=shadow_identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.15,
        )

        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=denied_rollout_identity,
        )

        self.assertEqual(rollout_state.phase, RolloutPhase.ROLLBACK_READY)
        self.assertTrue(rollout_state.rollback_required)
        self.assertEqual(rollout_state.promotion_signal.severity, "critical")

    def test_kki_recovery_orchestration_rolls_back_blocked_rollout(self) -> None:
        shadow_artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
        )
        shadow_plane = load_control_plane(shadow_artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-138",
        )
        work_unit = work_unit_for_state(
            state,
            title="rollback blocked rollout",
            boundary="rollout",
            correlation_id="corr-138-rollback",
            priority=WorkPriority.HIGH,
            budget_share=0.15,
        )
        shadow_identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )
        denied_rollout_identity = AuthorizationIdentity(
            slug="observer-rollout",
            kind=IdentityKind.OPERATOR,
            role=RoleName.OBSERVER,
            trust_level=TrustLevel.RESTRICTED,
            boundary_scope=("rollout",),
        )
        recovery_identity = AuthorizationIdentity(
            slug="supervisor-recovery",
            kind=IdentityKind.SUPERVISOR,
            role=RoleName.SUPERVISOR,
            trust_level=TrustLevel.PRIVILEGED,
            boundary_scope=("recovery", "rollout"),
        )
        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=shadow_plane,
            identity=shadow_identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.15,
        )
        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=denied_rollout_identity,
        )

        orchestration = orchestrate_recovery_for_rollout(
            rollout_state,
            control_plane=recovery_plane,
            identity=recovery_identity,
            evidence_ref="audit-recovery-rollback",
        )

        self.assertIsInstance(orchestration, RecoveryOrchestration)
        self.assertEqual(orchestration.mode, RecoveryMode.ROLLBACK)
        self.assertEqual(orchestration.disposition, RecoveryDisposition.CONTAIN)
        self.assertEqual(orchestration.outcome.status, "rollback-active")
        self.assertFalse(orchestration.resume_ready)

    def test_kki_recovery_orchestration_restarts_held_rollout(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        shadow_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-138",
            gates=GateReadiness(shadow=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="restart held rollout",
            boundary="rollout",
            correlation_id="corr-138-restart",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
        )
        shadow_identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )
        rollout_identity = AuthorizationIdentity(
            slug="gatekeeper-rollout",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("rollout", "governance"),
        )
        recovery_identity = AuthorizationIdentity(
            slug="supervisor-recovery",
            kind=IdentityKind.SUPERVISOR,
            role=RoleName.SUPERVISOR,
            trust_level=TrustLevel.PRIVILEGED,
            boundary_scope=("recovery", "rollout"),
        )
        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=shadow_plane,
            identity=shadow_identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.14,
        )
        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=rollout_identity,
            evidence_ref="audit-rollout-policy",
        )
        held_state = advance_rollout_state(rollout_state, phase=RolloutPhase.HELD, blockers=("manual hold",))

        orchestration = orchestrate_recovery_for_rollout(
            held_state,
            control_plane=recovery_plane,
            identity=recovery_identity,
            evidence_ref="audit-recovery-restart",
        )

        self.assertEqual(orchestration.mode, RecoveryMode.RESTART)
        self.assertEqual(orchestration.disposition, RecoveryDisposition.RESTART)
        self.assertEqual(orchestration.outcome.status, "restart-active")
        self.assertFalse(orchestration.resume_ready)

    def test_kki_recovery_orchestration_prepares_reentry_for_canary(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        shadow_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-138",
        )
        work_unit = work_unit_for_state(
            state,
            title="reentry canary",
            boundary="rollout",
            correlation_id="corr-138-reentry",
            priority=WorkPriority.HIGH,
            budget_share=0.12,
        )
        replay_unit = advance_work_unit(
            work_unit,
            status=WorkStatus.HANDED_OFF,
            attempt=1,
            handoff_ref="handoff-reentry",
        )
        shadow_identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )
        rollout_identity = AuthorizationIdentity(
            slug="gatekeeper-rollout",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("rollout", "governance"),
        )
        recovery_identity = AuthorizationIdentity(
            slug="supervisor-recovery",
            kind=IdentityKind.SUPERVISOR,
            role=RoleName.SUPERVISOR,
            trust_level=TrustLevel.PRIVILEGED,
            boundary_scope=("recovery", "rollout"),
        )
        coordination = coordinate_shadow_work(
            state,
            replay_unit,
            control_plane=shadow_plane,
            identity=shadow_identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.12,
        )
        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=rollout_identity,
            evidence_ref="audit-rollout-policy",
        )

        orchestration = orchestrate_recovery_for_rollout(
            rollout_state,
            control_plane=recovery_plane,
            identity=recovery_identity,
            evidence_ref="audit-recovery-reentry",
        )

        self.assertEqual(orchestration.mode, RecoveryMode.REENTRY)
        self.assertEqual(orchestration.disposition, RecoveryDisposition.RESUME)
        self.assertEqual(orchestration.outcome.status, "reentry-ready")
        self.assertTrue(orchestration.resume_ready)

    def test_kki_recovery_orchestration_blocks_resume_without_recovery_authority(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        shadow_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-138",
        )
        work_unit = work_unit_for_state(
            state,
            title="blocked resume",
            boundary="rollout",
            correlation_id="corr-138-blocked",
            priority=WorkPriority.HIGH,
            budget_share=0.12,
        )
        replay_unit = advance_work_unit(
            work_unit,
            status=WorkStatus.HANDED_OFF,
            attempt=1,
            handoff_ref="handoff-blocked-resume",
        )
        shadow_identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )
        rollout_identity = AuthorizationIdentity(
            slug="gatekeeper-rollout",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("rollout", "governance"),
        )
        denied_recovery_identity = AuthorizationIdentity(
            slug="observer-recovery",
            kind=IdentityKind.OPERATOR,
            role=RoleName.OBSERVER,
            trust_level=TrustLevel.RESTRICTED,
            boundary_scope=("recovery",),
        )
        coordination = coordinate_shadow_work(
            state,
            replay_unit,
            control_plane=shadow_plane,
            identity=shadow_identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.12,
        )
        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=rollout_identity,
            evidence_ref="audit-rollout-policy",
        )

        orchestration = orchestrate_recovery_for_rollout(
            rollout_state,
            control_plane=recovery_plane,
            identity=denied_recovery_identity,
            evidence_ref="audit-recovery-blocked",
        )

        self.assertEqual(orchestration.gate_decision.outcome, GateOutcome.BLOCK)
        self.assertFalse(orchestration.resume_ready)
        self.assertEqual(orchestration.recovery_signal.severity, "info")

    def test_kki_human_governance_approves_reentry_release(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        shadow_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        governance_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="governance")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-139",
        )
        work_unit = work_unit_for_state(
            state,
            title="govern reentry",
            boundary="rollout",
            correlation_id="corr-139-approve",
            priority=WorkPriority.HIGH,
            budget_share=0.12,
        )
        replay_unit = advance_work_unit(
            work_unit,
            status=WorkStatus.HANDED_OFF,
            attempt=1,
            handoff_ref="handoff-govern-approve",
        )
        shadow_identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )
        rollout_identity = AuthorizationIdentity(
            slug="gatekeeper-rollout",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("rollout", "governance"),
        )
        recovery_identity = AuthorizationIdentity(
            slug="supervisor-recovery",
            kind=IdentityKind.SUPERVISOR,
            role=RoleName.SUPERVISOR,
            trust_level=TrustLevel.PRIVILEGED,
            boundary_scope=("recovery", "rollout"),
        )
        governance_identity = AuthorizationIdentity(
            slug="gatekeeper-governance",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("governance", "rollout"),
        )
        coordination = coordinate_shadow_work(
            state,
            replay_unit,
            control_plane=shadow_plane,
            identity=shadow_identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.12,
        )
        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=rollout_identity,
            evidence_ref="audit-rollout-policy",
        )
        recovery = orchestrate_recovery_for_rollout(
            rollout_state,
            control_plane=recovery_plane,
            identity=recovery_identity,
            evidence_ref="audit-recovery-approve",
        )

        governance = govern_recovery_orchestration(
            recovery,
            control_plane=governance_plane,
            identity=governance_identity,
            decision=HumanDecision.APPROVE,
            audit_ref="audit-governance-approve",
        )

        self.assertIsInstance(governance, HumanLoopGovernance)
        self.assertEqual(governance.gate_decision.outcome, GateOutcome.GO)
        self.assertTrue(governance.release_authorized)
        self.assertEqual(governance.governance_signal.status, "authorized")

    def test_kki_human_governance_holds_restart_path(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        shadow_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        governance_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="governance")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-139",
            gates=GateReadiness(shadow=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="govern hold",
            boundary="rollout",
            correlation_id="corr-139-hold",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
        )
        shadow_identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )
        rollout_identity = AuthorizationIdentity(
            slug="gatekeeper-rollout",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("rollout", "governance"),
        )
        recovery_identity = AuthorizationIdentity(
            slug="supervisor-recovery",
            kind=IdentityKind.SUPERVISOR,
            role=RoleName.SUPERVISOR,
            trust_level=TrustLevel.PRIVILEGED,
            boundary_scope=("recovery", "rollout"),
        )
        governance_identity = AuthorizationIdentity(
            slug="gatekeeper-governance",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("governance", "rollout"),
        )
        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=shadow_plane,
            identity=shadow_identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.14,
        )
        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=rollout_identity,
            evidence_ref="audit-rollout-policy",
        )
        held_state = advance_rollout_state(rollout_state, phase=RolloutPhase.HELD, blockers=("manual hold",))
        recovery = orchestrate_recovery_for_rollout(
            held_state,
            control_plane=recovery_plane,
            identity=recovery_identity,
            evidence_ref="audit-recovery-hold",
        )

        governance = govern_recovery_orchestration(
            recovery,
            control_plane=governance_plane,
            identity=governance_identity,
            decision=HumanDecision.HOLD,
            audit_ref="audit-governance-hold",
        )

        self.assertFalse(governance.release_authorized)
        self.assertEqual(governance.governance_signal.status, "held")
        self.assertEqual(governance.governance_signal.severity, "warning")

    def test_kki_human_governance_escalates_when_requested(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        shadow_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        governance_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="governance")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-139",
            gates=GateReadiness(shadow=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="govern escalate",
            boundary="rollout",
            correlation_id="corr-139-escalate",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
        )
        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=shadow_plane,
            identity=AuthorizationIdentity(
                slug="executor-shadow",
                kind=IdentityKind.MODULE,
                role=RoleName.EXECUTOR,
                trust_level=TrustLevel.VERIFIED,
                boundary_scope=("shadow", "rollout"),
            ),
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.14,
        )
        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=AuthorizationIdentity(
                slug="gatekeeper-rollout",
                kind=IdentityKind.OPERATOR,
                role=RoleName.GATEKEEPER,
                trust_level=TrustLevel.VERIFIED,
                boundary_scope=("rollout", "governance"),
            ),
            evidence_ref="audit-rollout-policy",
        )
        held_state = advance_rollout_state(rollout_state, phase=RolloutPhase.HELD, blockers=("manual escalation",))
        recovery = orchestrate_recovery_for_rollout(
            held_state,
            control_plane=recovery_plane,
            identity=AuthorizationIdentity(
                slug="supervisor-recovery",
                kind=IdentityKind.SUPERVISOR,
                role=RoleName.SUPERVISOR,
                trust_level=TrustLevel.PRIVILEGED,
                boundary_scope=("recovery", "rollout"),
            ),
            evidence_ref="audit-recovery-escalate",
        )
        governance = govern_recovery_orchestration(
            recovery,
            control_plane=governance_plane,
            identity=AuthorizationIdentity(
                slug="gatekeeper-governance",
                kind=IdentityKind.OPERATOR,
                role=RoleName.GATEKEEPER,
                trust_level=TrustLevel.VERIFIED,
                boundary_scope=("governance", "rollout"),
            ),
            decision=HumanDecision.ESCALATE,
            audit_ref="audit-governance-escalate",
        )

        self.assertFalse(governance.release_authorized)
        self.assertEqual(governance.governance_signal.status, "escalated")
        self.assertEqual(governance.governance_signal.severity, "warning")

    def test_kki_human_governance_override_requires_commitment(self) -> None:
        governance_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="governance")
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-139",
        )
        work_unit = work_unit_for_state(
            state,
            title="override path",
            boundary="rollout",
            correlation_id="corr-139-override",
            priority=WorkPriority.HIGH,
            budget_share=0.12,
        )
        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="shadow"),
            identity=AuthorizationIdentity(
                slug="executor-shadow",
                kind=IdentityKind.MODULE,
                role=RoleName.EXECUTOR,
                trust_level=TrustLevel.VERIFIED,
                boundary_scope=("shadow", "rollout"),
            ),
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.12,
        )
        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="rollout"),
            identity=AuthorizationIdentity(
                slug="observer-rollout",
                kind=IdentityKind.OPERATOR,
                role=RoleName.OBSERVER,
                trust_level=TrustLevel.RESTRICTED,
                boundary_scope=("rollout",),
            ),
        )
        recovery = orchestrate_recovery_for_rollout(
            rollout_state,
            control_plane=recovery_plane,
            identity=AuthorizationIdentity(
                slug="supervisor-recovery",
                kind=IdentityKind.SUPERVISOR,
                role=RoleName.SUPERVISOR,
                trust_level=TrustLevel.PRIVILEGED,
                boundary_scope=("recovery", "rollout"),
            ),
            evidence_ref="audit-recovery-override",
        )
        denied = govern_recovery_orchestration(
            recovery,
            control_plane=governance_plane,
            identity=AuthorizationIdentity(
                slug="supervisor-governance",
                kind=IdentityKind.SUPERVISOR,
                role=RoleName.SUPERVISOR,
                trust_level=TrustLevel.EMERGENCY,
                boundary_scope=("governance", "recovery"),
            ),
            decision=HumanDecision.OVERRIDE,
            audit_ref="audit-governance-override",
        )
        allowed = govern_recovery_orchestration(
            recovery,
            control_plane=governance_plane,
            identity=AuthorizationIdentity(
                slug="supervisor-governance",
                kind=IdentityKind.SUPERVISOR,
                role=RoleName.SUPERVISOR,
                trust_level=TrustLevel.EMERGENCY,
                boundary_scope=("governance", "recovery"),
            ),
            decision=HumanDecision.OVERRIDE,
            audit_ref="audit-governance-override",
            commitment_ref="commit-override",
        )

        self.assertEqual(denied.gate_decision.outcome, GateOutcome.BLOCK)
        self.assertFalse(denied.release_authorized)
        self.assertEqual(allowed.gate_decision.outcome, GateOutcome.ESCALATE)
        self.assertTrue(allowed.release_authorized)
        self.assertEqual(allowed.governance_signal.status, "authorized-override")

    def test_kki_integrated_operations_run_succeeds(self) -> None:
        run = run_integrated_operations(correlation_id="corr-140-ops")

        self.assertIsInstance(run, IntegratedOperationsRun)
        self.assertTrue(run.success)
        self.assertTrue(run.shadow_coordination.release_ready)
        self.assertTrue(run.rollout_state.promotion_ready)
        self.assertTrue(run.recovery_orchestration.resume_ready)
        self.assertTrue(run.human_governance.release_authorized)

    def test_kki_integrated_operations_run_exposes_full_chain(self) -> None:
        run = run_integrated_operations(correlation_id="corr-140-chain")

        self.assertEqual(run.work_unit.correlation_id, "corr-140-chain")
        self.assertEqual(run.shadow_coordination.work_unit.unit_id, run.work_unit.unit_id)
        self.assertEqual(run.rollout_state.work_unit_id, run.work_unit.unit_id)
        self.assertEqual(run.recovery_orchestration.rollout_state.work_unit_id, run.work_unit.unit_id)
        self.assertEqual(run.human_governance.subject_ref, run.recovery_orchestration.orchestration_id)

    def test_kki_integrated_operations_snapshot_contains_all_signals(self) -> None:
        run = run_integrated_operations(correlation_id="corr-140-snapshot")

        signal_names = [signal.signal_name for signal in run.final_snapshot.signals]
        self.assertIn("shadow-release", signal_names)
        self.assertIn("rollout-phase", signal_names)
        self.assertIn("recovery-orchestration", signal_names)
        self.assertIn("human-governance", signal_names)
        self.assertEqual(run.final_snapshot.highest_severity(), "info")

    def test_kki_integrated_operations_run_serializes_success(self) -> None:
        payload = run_integrated_operations(correlation_id="corr-140-dict").to_dict()

        self.assertTrue(payload["success"])
        self.assertEqual(payload["mission_profile"]["mission_ref"], "operations-run")
        self.assertEqual(payload["shadow_coordination"]["work_unit"]["correlation_id"], "corr-140-dict")
        self.assertEqual(payload["human_governance"]["decision"], "approve")

    def test_kki_mission_profile_preset_is_typed(self) -> None:
        mission = mission_profile_for_name("pilot-cutover")

        self.assertIsInstance(mission, MissionProfile)
        self.assertEqual(mission.scenario, MissionScenario.CUTOVER)
        self.assertEqual(mission.runtime_stage, RuntimeStage.PILOT)
        self.assertEqual(mission.policy.promotion_gate, "hold-until-shadow-green")
        self.assertEqual(mission.available_roles, (RoleName.EXECUTOR,))

    def test_kki_mission_profile_catalog_lists_presets(self) -> None:
        self.assertEqual(
            mission_profile_catalog(),
            ("pilot-cutover", "shadow-hardening", "recovery-drill"),
        )

    def test_kki_integrated_operations_run_accepts_named_mission_profile(self) -> None:
        run = run_integrated_operations(mission="pilot-cutover", correlation_id="corr-141-pilot")

        self.assertEqual(run.mission_profile.mission_ref, "pilot-cutover")
        self.assertEqual(run.orchestration_state.mission_ref, "pilot-cutover")
        self.assertEqual(run.runtime_dna.identity.profile, "pilot-runtime-dna")
        self.assertEqual(run.shadow_control_plane.effective_payload["mission_ref"], "pilot-cutover")
        self.assertEqual(run.work_unit.labels["mission_scenario"], "cutover")

    def test_kki_integrated_operations_run_uses_custom_mission_profile(self) -> None:
        run = run_integrated_operations(
            mission=MissionProfile(
                mission_ref="custom-hardening",
                title="custom hardening run",
                scenario=MissionScenario.HARDENING,
                runtime_stage=RuntimeStage.SHADOW,
                runtime_profile="resilient-runtime-dna",
                target_boundary=ModuleBoundaryName.ROLLOUT,
                work_priority=WorkPriority.CRITICAL,
                budget_share=0.14,
                observed_budget=0.13,
                policy=MissionPolicy(
                    resource_budget=0.81,
                    recovery_reserve=0.22,
                    drift_threshold=0.02,
                    promotion_gate="strict-shadow-window",
                ),
                labels={"campaign": "custom"},
            ),
            correlation_id="corr-141-custom",
        )

        self.assertEqual(run.mission_profile.mission_ref, "custom-hardening")
        self.assertEqual(run.runtime_dna.identity.stage, RuntimeStage.SHADOW)
        self.assertEqual(run.work_unit.priority, WorkPriority.CRITICAL)
        self.assertEqual(run.shadow_control_plane.effective_payload["drift_threshold"], 0.02)
        self.assertEqual(run.rollout_control_plane.effective_payload["promotion_gate"], "strict-shadow-window")

    def test_kki_operations_wave_executes_admitted_runs(self) -> None:
        wave = run_operations_wave(
            (
                "pilot-cutover",
                MissionProfile(
                    mission_ref="pilot-hardening",
                    title="pilot hardening pass",
                    scenario=MissionScenario.HARDENING,
                    runtime_stage=RuntimeStage.PILOT,
                    runtime_profile="pilot-runtime-dna",
                    target_boundary=ModuleBoundaryName.ROLLOUT,
                    work_priority=WorkPriority.HIGH,
                    budget_share=0.11,
                    observed_budget=0.1,
                    labels={"campaign": "pilot"},
                ),
            ),
            wave_id="wave-142-pilot",
        )

        self.assertIsInstance(wave, OperationsWave)
        self.assertEqual(len(wave.admitted_mission_refs), 2)
        self.assertEqual(wave.wave_signal.status, "executed")
        self.assertTrue(wave.success)

    def test_kki_operations_wave_holds_work_when_budget_exhausted(self) -> None:
        wave = run_operations_wave(
            (
                MissionProfile(
                    mission_ref="pilot-critical",
                    title="pilot critical cutover",
                    scenario=MissionScenario.CUTOVER,
                    runtime_stage=RuntimeStage.PILOT,
                    runtime_profile="pilot-runtime-dna",
                    target_boundary=ModuleBoundaryName.ROLLOUT,
                    work_priority=WorkPriority.CRITICAL,
                    budget_share=0.14,
                    observed_budget=0.14,
                ),
                MissionProfile(
                    mission_ref="pilot-normal",
                    title="pilot normal rollout",
                    scenario=MissionScenario.ROUTINE,
                    runtime_stage=RuntimeStage.PILOT,
                    runtime_profile="pilot-runtime-dna",
                    target_boundary=ModuleBoundaryName.ROLLOUT,
                    work_priority=WorkPriority.NORMAL,
                    budget_share=0.13,
                    observed_budget=0.12,
                ),
            ),
            wave_id="wave-142-budget",
            budget_policy=WaveBudgetPolicy(total_budget=0.3, reserve_floor=0.12, max_parallel=2),
        )

        self.assertEqual(wave.admitted_mission_refs, ("pilot-critical",))
        self.assertEqual(wave.held_mission_refs, ("pilot-normal",))
        self.assertEqual(wave.wave_signal.status, "partial")

    def test_kki_operations_wave_rejects_mixed_runtime_stages(self) -> None:
        with self.assertRaises(ValueError):
            run_operations_wave(("pilot-cutover", "shadow-hardening"), wave_id="wave-142-mixed")

    def test_kki_operations_wave_snapshot_contains_wave_signal(self) -> None:
        wave = run_operations_wave(("pilot-cutover",), wave_id="wave-142-signal")

        signal_names = [signal.signal_name for signal in wave.final_snapshot.signals]
        self.assertIn("operations-wave", signal_names)
        self.assertIn("shadow-release", signal_names)
        self.assertEqual(wave.wave_signal.status, "executed")
        self.assertTrue(wave.to_dict()["success"])

    def test_kki_run_ledger_compiles_entries_for_wave(self) -> None:
        ledger = ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-143-ledger"))

        self.assertIsInstance(ledger, OperationsRunLedger)
        self.assertEqual(len(ledger.entries), 1)
        self.assertIsInstance(ledger.entries[0], RunLedgerEntry)
        self.assertEqual(ledger.executed_mission_refs, ("pilot-cutover",))

    def test_kki_run_ledger_preserves_held_wave_entries(self) -> None:
        ledger = ledger_for_wave(
            run_operations_wave(
                (
                    MissionProfile(
                        mission_ref="ledger-critical",
                        title="ledger critical",
                        scenario=MissionScenario.CUTOVER,
                        runtime_stage=RuntimeStage.PILOT,
                        runtime_profile="pilot-runtime-dna",
                        target_boundary=ModuleBoundaryName.ROLLOUT,
                        work_priority=WorkPriority.CRITICAL,
                        budget_share=0.14,
                    ),
                    MissionProfile(
                        mission_ref="ledger-held",
                        title="ledger held",
                        scenario=MissionScenario.ROUTINE,
                        runtime_stage=RuntimeStage.PILOT,
                        runtime_profile="pilot-runtime-dna",
                        target_boundary=ModuleBoundaryName.ROLLOUT,
                        work_priority=WorkPriority.NORMAL,
                        budget_share=0.13,
                    ),
                ),
                wave_id="wave-143-held",
                budget_policy=WaveBudgetPolicy(total_budget=0.3, reserve_floor=0.12, max_parallel=2),
            )
        )

        self.assertEqual(ledger.executed_mission_refs, ("ledger-critical",))
        self.assertEqual(ledger.held_mission_refs, ("ledger-held",))
        held_entry = next(entry for entry in ledger.entries if entry.mission_ref == "ledger-held")
        self.assertFalse(held_entry.executed)
        self.assertEqual(held_entry.governance_status, "not-executed")

    def test_kki_run_ledger_snapshot_contains_ledger_signal(self) -> None:
        ledger = ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-143-signal"))

        signal_names = [signal.signal_name for signal in ledger.final_snapshot.signals]
        self.assertIn("run-ledger", signal_names)
        self.assertIn("operations-wave", signal_names)
        self.assertEqual(ledger.wave_signal.status, "compiled")

    def test_kki_run_ledger_serializes_status_counts(self) -> None:
        payload = ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-143-dict")).to_dict()

        self.assertEqual(payload["status_counts"]["admit"], 1)
        self.assertEqual(payload["entries"][0]["mission_ref"], "pilot-cutover")

    def test_kki_incident_report_is_clear_for_clean_wave(self) -> None:
        report = detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-144-clear")))

        self.assertIsInstance(report, IncidentReport)
        self.assertEqual(report.incidents, ())
        self.assertEqual(report.incident_signal.status, "clear")
        self.assertEqual(report.escalation_mission_refs, ())

    def test_kki_incident_report_detects_dispatch_hold(self) -> None:
        report = detect_incidents(
            ledger_for_wave(
                run_operations_wave(
                    (
                        MissionProfile(
                            mission_ref="incident-critical",
                            title="incident critical",
                            scenario=MissionScenario.CUTOVER,
                            runtime_stage=RuntimeStage.PILOT,
                            runtime_profile="pilot-runtime-dna",
                            target_boundary=ModuleBoundaryName.ROLLOUT,
                            work_priority=WorkPriority.CRITICAL,
                            budget_share=0.14,
                        ),
                        MissionProfile(
                            mission_ref="incident-held",
                            title="incident held",
                            scenario=MissionScenario.ROUTINE,
                            runtime_stage=RuntimeStage.PILOT,
                            runtime_profile="pilot-runtime-dna",
                            target_boundary=ModuleBoundaryName.ROLLOUT,
                            work_priority=WorkPriority.NORMAL,
                            budget_share=0.13,
                        ),
                    ),
                    wave_id="wave-144-held",
                    budget_policy=WaveBudgetPolicy(total_budget=0.3, reserve_floor=0.12, max_parallel=2),
                )
            )
        )

        self.assertEqual(len(report.incidents), 1)
        self.assertEqual(report.incidents[0].cause, IncidentCause.DISPATCH)
        self.assertEqual(report.incidents[0].severity, IncidentSeverity.WARNING)
        self.assertEqual(report.escalation_mission_refs, ("incident-held",))

    def test_kki_incident_report_detects_governance_escalation(self) -> None:
        report = detect_incidents(
            ledger_for_wave(
                run_operations_wave(
                    (
                        MissionProfile(
                            mission_ref="incident-governance",
                            title="incident governance",
                            scenario=MissionScenario.CUTOVER,
                            runtime_stage=RuntimeStage.PILOT,
                            runtime_profile="pilot-runtime-dna",
                            target_boundary=ModuleBoundaryName.ROLLOUT,
                            governance_decision=HumanDecision.ESCALATE,
                        ),
                    ),
                    wave_id="wave-144-governance",
                )
            )
        )

        self.assertEqual(len(report.incidents), 1)
        self.assertEqual(report.incidents[0].cause, IncidentCause.GOVERNANCE)
        self.assertEqual(report.incident_signal.status, "attention-required")

    def test_kki_incident_report_serializes_critical_entries(self) -> None:
        manual_report = IncidentReport(
            wave_id="wave-144-manual",
            ledger=ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-144-base")),
            incidents=(
                OperationsIncident(
                    incident_id="incident-wave-144-manual-critical",
                    wave_id="wave-144-manual",
                    severity=IncidentSeverity.CRITICAL,
                    cause=IncidentCause.RECOVERY,
                    summary="manual critical recovery incident",
                    mission_refs=("pilot-cutover",),
                    trigger_statuses=("rollback-active",),
                    escalation_required=True,
                ),
            ),
            incident_signal=TelemetrySignal(
                signal_name="incident-report",
                boundary=ModuleBoundaryName.TELEMETRY,
                correlation_id="wave-144-manual",
                severity="critical",
                status="critical-incidents",
            ),
            final_snapshot=build_telemetry_snapshot(
                runtime_stage=RuntimeStage.PILOT,
                signals=(
                    TelemetrySignal(
                        signal_name="incident-report",
                        boundary=ModuleBoundaryName.TELEMETRY,
                        correlation_id="wave-144-manual",
                        severity="critical",
                        status="critical-incidents",
                    ),
                ),
            ),
        ).to_dict()

        self.assertEqual(manual_report["critical_incidents"][0]["cause"], "recovery")
        self.assertEqual(manual_report["escalation_mission_refs"], ["pilot-cutover"])

    def test_kki_escalation_plan_is_clear_without_incidents(self) -> None:
        plan = coordinate_escalations(
            detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-145-clear")))
        )

        self.assertIsInstance(plan, EscalationPlan)
        self.assertEqual(plan.directives, ())
        self.assertEqual(plan.escalation_signal.status, "clear")

    def test_kki_escalation_plan_replans_dispatch_holds(self) -> None:
        plan = coordinate_escalations(
            detect_incidents(
                ledger_for_wave(
                    run_operations_wave(
                        (
                            MissionProfile(
                                mission_ref="escalation-critical",
                                title="escalation critical",
                                scenario=MissionScenario.CUTOVER,
                                runtime_stage=RuntimeStage.PILOT,
                                runtime_profile="pilot-runtime-dna",
                                target_boundary=ModuleBoundaryName.ROLLOUT,
                                work_priority=WorkPriority.CRITICAL,
                                budget_share=0.14,
                            ),
                            MissionProfile(
                                mission_ref="escalation-held",
                                title="escalation held",
                                scenario=MissionScenario.ROUTINE,
                                runtime_stage=RuntimeStage.PILOT,
                                runtime_profile="pilot-runtime-dna",
                                target_boundary=ModuleBoundaryName.ROLLOUT,
                                work_priority=WorkPriority.NORMAL,
                                budget_share=0.13,
                            ),
                        ),
                        wave_id="wave-145-dispatch",
                        budget_policy=WaveBudgetPolicy(total_budget=0.3, reserve_floor=0.12, max_parallel=2),
                    )
                )
            )
        )

        self.assertEqual(len(plan.directives), 1)
        self.assertIsInstance(plan.directives[0], EscalationDirective)
        self.assertEqual(plan.directives[0].path, EscalationPath.DISPATCH_REPLAN)
        self.assertEqual(plan.blocked_release_refs, ("escalation-held",))

    def test_kki_escalation_plan_routes_governance_review(self) -> None:
        plan = coordinate_escalations(
            detect_incidents(
                ledger_for_wave(
                    run_operations_wave(
                        (
                            MissionProfile(
                                mission_ref="escalation-governance",
                                title="escalation governance",
                                scenario=MissionScenario.CUTOVER,
                                runtime_stage=RuntimeStage.PILOT,
                                runtime_profile="pilot-runtime-dna",
                                target_boundary=ModuleBoundaryName.ROLLOUT,
                                governance_decision=HumanDecision.ESCALATE,
                            ),
                        ),
                        wave_id="wave-145-governance",
                    )
                )
            )
        )

        self.assertEqual(plan.directives[0].path, EscalationPath.GOVERNANCE_REVIEW)
        self.assertEqual(plan.governance_review_refs, ("escalation-governance",))
        self.assertEqual(plan.escalation_signal.status, "response-required")

    def test_kki_escalation_plan_contains_critical_recovery_response(self) -> None:
        base_report = detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-145-base")))
        critical_report = IncidentReport(
            wave_id=base_report.wave_id,
            ledger=base_report.ledger,
            incidents=(
                OperationsIncident(
                    incident_id="incident-wave-145-critical-recovery",
                    wave_id=base_report.wave_id,
                    severity=IncidentSeverity.CRITICAL,
                    cause=IncidentCause.RECOVERY,
                    summary="critical recovery rollback incident",
                    mission_refs=("pilot-cutover",),
                    trigger_statuses=("rollback-active",),
                    escalation_required=True,
                ),
            ),
            incident_signal=TelemetrySignal(
                signal_name="incident-report",
                boundary=ModuleBoundaryName.TELEMETRY,
                correlation_id=base_report.wave_id,
                severity="critical",
                status="critical-incidents",
            ),
            final_snapshot=base_report.final_snapshot,
        )
        plan = coordinate_escalations(critical_report)

        self.assertEqual(plan.directives[0].path, EscalationPath.ROLLBACK_CONTAINMENT)
        self.assertEqual(plan.directives[0].recovery_disposition, RecoveryDisposition.CONTAIN)
        self.assertEqual(plan.escalation_signal.status, "critical-response")

    def test_kki_change_window_opens_for_clean_plan(self) -> None:
        window = open_change_window(
            (
                coordinate_escalations(
                    detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-146-open")))
                ),
            ),
            window_id="window-146-open",
        )

        self.assertIsInstance(window, ChangeWindow)
        self.assertIsInstance(window.entries[0], ChangeWindowEntry)
        self.assertEqual(window.status, ChangeWindowStatus.OPEN)
        self.assertEqual(window.allowed_promotions, ("pilot-cutover",))

    def test_kki_change_window_guards_governance_review(self) -> None:
        plan = coordinate_escalations(
            detect_incidents(
                ledger_for_wave(
                    run_operations_wave(
                        (
                            MissionProfile(
                                mission_ref="window-governance",
                                title="window governance",
                                scenario=MissionScenario.CUTOVER,
                                runtime_stage=RuntimeStage.PILOT,
                                runtime_profile="pilot-runtime-dna",
                                target_boundary=ModuleBoundaryName.ROLLOUT,
                                governance_decision=HumanDecision.ESCALATE,
                            ),
                        ),
                        wave_id="wave-146-guarded",
                    )
                )
            )
        )
        window = open_change_window((plan,), window_id="window-146-guarded")

        self.assertEqual(window.status, ChangeWindowStatus.GUARDED)
        self.assertEqual(window.blocked_refs, ("window-governance",))

    def test_kki_change_window_sets_recovery_only_mode(self) -> None:
        base_report = detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-146-recovery")))
        recovery_plan = coordinate_escalations(
            IncidentReport(
                wave_id=base_report.wave_id,
                ledger=base_report.ledger,
                incidents=(
                    OperationsIncident(
                        incident_id="incident-wave-146-restart",
                        wave_id=base_report.wave_id,
                        severity=IncidentSeverity.WARNING,
                        cause=IncidentCause.RECOVERY,
                        summary="restart recovery path",
                        mission_refs=("pilot-cutover",),
                        trigger_statuses=("restart-active",),
                        escalation_required=True,
                    ),
                ),
                incident_signal=TelemetrySignal(
                    signal_name="incident-report",
                    boundary=ModuleBoundaryName.TELEMETRY,
                    correlation_id=base_report.wave_id,
                    severity="warning",
                    status="attention-required",
                ),
                final_snapshot=base_report.final_snapshot,
            )
        )
        window = open_change_window((recovery_plan,), window_id="window-146-recovery")

        self.assertEqual(window.status, ChangeWindowStatus.RECOVERY_ONLY)
        self.assertEqual(window.recovery_only_refs, ("pilot-cutover",))

    def test_kki_change_window_blocks_critical_containment(self) -> None:
        base_report = detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-146-blocked")))
        critical_plan = coordinate_escalations(
            IncidentReport(
                wave_id=base_report.wave_id,
                ledger=base_report.ledger,
                incidents=(
                    OperationsIncident(
                        incident_id="incident-wave-146-critical",
                        wave_id=base_report.wave_id,
                        severity=IncidentSeverity.CRITICAL,
                        cause=IncidentCause.RECOVERY,
                        summary="critical rollback containment",
                        mission_refs=("pilot-cutover",),
                        trigger_statuses=("rollback-active",),
                        escalation_required=True,
                    ),
                ),
                incident_signal=TelemetrySignal(
                    signal_name="incident-report",
                    boundary=ModuleBoundaryName.TELEMETRY,
                    correlation_id=base_report.wave_id,
                    severity="critical",
                    status="critical-incidents",
                ),
                final_snapshot=base_report.final_snapshot,
            )
        )
        window = open_change_window((critical_plan,), window_id="window-146-blocked")

        self.assertEqual(window.status, ChangeWindowStatus.BLOCKED)
        self.assertEqual(window.blocked_refs, ("pilot-cutover",))

    def test_kki_release_campaign_builds_ready_promotion_path(self) -> None:
        window = open_change_window(
            (
                coordinate_escalations(
                    detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-147-ready")))
                ),
            ),
            window_id="window-147-ready",
        )
        campaign = build_release_campaign((window,), campaign_id="campaign-147-ready")

        self.assertIsInstance(campaign, ReleaseCampaign)
        self.assertIsInstance(campaign.stages[0], ReleaseCampaignStage)
        self.assertEqual(campaign.status, ReleaseCampaignStatus.READY)
        self.assertEqual(campaign.promotion_refs, ("pilot-cutover",))
        self.assertIn(ReleaseCampaignStageType.PROMOTION_WAVE, {stage.stage_type for stage in campaign.stages})

    def test_kki_release_campaign_routes_governance_review_stage(self) -> None:
        window = open_change_window(
            (
                coordinate_escalations(
                    detect_incidents(
                        ledger_for_wave(
                            run_operations_wave(
                                (
                                    MissionProfile(
                                        mission_ref="campaign-governance",
                                        title="campaign governance",
                                        scenario=MissionScenario.CUTOVER,
                                        runtime_stage=RuntimeStage.PILOT,
                                        runtime_profile="pilot-runtime-dna",
                                        target_boundary=ModuleBoundaryName.ROLLOUT,
                                        governance_decision=HumanDecision.ESCALATE,
                                    ),
                                ),
                                wave_id="wave-147-guarded",
                            )
                        )
                    )
                ),
            ),
            window_id="window-147-guarded",
        )
        campaign = build_release_campaign((window,), campaign_id="campaign-147-guarded")

        self.assertEqual(campaign.status, ReleaseCampaignStatus.GUARDED)
        self.assertEqual(campaign.governance_review_refs, ("campaign-governance",))
        self.assertIn(ReleaseCampaignStageType.GOVERNANCE_REVIEW, {stage.stage_type for stage in campaign.stages})

    def test_kki_release_campaign_preserves_recovery_only_stage(self) -> None:
        base_report = detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-147-recovery")))
        recovery_plan = coordinate_escalations(
            IncidentReport(
                wave_id=base_report.wave_id,
                ledger=base_report.ledger,
                incidents=(
                    OperationsIncident(
                        incident_id="incident-wave-147-restart",
                        wave_id=base_report.wave_id,
                        severity=IncidentSeverity.WARNING,
                        cause=IncidentCause.RECOVERY,
                        summary="restart recovery path",
                        mission_refs=("pilot-cutover",),
                        trigger_statuses=("restart-active",),
                        escalation_required=True,
                    ),
                ),
                incident_signal=TelemetrySignal(
                    signal_name="incident-report",
                    boundary=ModuleBoundaryName.TELEMETRY,
                    correlation_id=base_report.wave_id,
                    severity="warning",
                    status="attention-required",
                ),
                final_snapshot=base_report.final_snapshot,
            )
        )
        window = open_change_window((recovery_plan,), window_id="window-147-recovery")
        campaign = build_release_campaign((window,), campaign_id="campaign-147-recovery")

        self.assertEqual(campaign.status, ReleaseCampaignStatus.RECOVERY_ONLY)
        self.assertEqual(campaign.recovery_only_refs, ("pilot-cutover",))
        self.assertNotIn(ReleaseCampaignStageType.PROMOTION_WAVE, {stage.stage_type for stage in campaign.stages})
        self.assertIn(ReleaseCampaignStageType.RECOVERY_WAVE, {stage.stage_type for stage in campaign.stages})

    def test_kki_release_campaign_blocks_containment_stage(self) -> None:
        base_report = detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-147-blocked")))
        critical_plan = coordinate_escalations(
            IncidentReport(
                wave_id=base_report.wave_id,
                ledger=base_report.ledger,
                incidents=(
                    OperationsIncident(
                        incident_id="incident-wave-147-critical",
                        wave_id=base_report.wave_id,
                        severity=IncidentSeverity.CRITICAL,
                        cause=IncidentCause.RECOVERY,
                        summary="critical rollback containment",
                        mission_refs=("pilot-cutover",),
                        trigger_statuses=("rollback-active",),
                        escalation_required=True,
                    ),
                ),
                incident_signal=TelemetrySignal(
                    signal_name="incident-report",
                    boundary=ModuleBoundaryName.TELEMETRY,
                    correlation_id=base_report.wave_id,
                    severity="critical",
                    status="critical-incidents",
                ),
                final_snapshot=base_report.final_snapshot,
            )
        )
        window = open_change_window((critical_plan,), window_id="window-147-blocked")
        campaign = build_release_campaign((window,), campaign_id="campaign-147-blocked")

        self.assertEqual(campaign.status, ReleaseCampaignStatus.BLOCKED)
        self.assertEqual(campaign.blocked_refs, ("pilot-cutover",))
        self.assertIn(ReleaseCampaignStageType.CONTAINMENT, {stage.stage_type for stage in campaign.stages})

    def test_kki_benchmark_case_matrix_exposes_canonical_cases(self) -> None:
        cases = benchmark_case_matrix()

        self.assertEqual(len(cases), 4)
        self.assertIsInstance(cases[0], BenchmarkCase)
        self.assertEqual(
            tuple(case.case_id for case in cases),
            ("pilot-ready", "shadow-guarded", "recovery-resume", "pilot-containment"),
        )

    def test_kki_benchmark_harness_runs_ready_case(self) -> None:
        case = BenchmarkCase(
            case_id="benchmark-ready",
            title="benchmark ready",
            missions=(mission_profile_for_name("pilot-cutover"),),
            release_mode=BenchmarkReleaseMode.READY,
        )
        harness = run_benchmark_harness((case,), harness_id="harness-148-ready")

        self.assertIsInstance(harness, BenchmarkHarness)
        self.assertEqual(harness.results[0].status, ReleaseCampaignStatus.READY)
        self.assertEqual(harness.results[0].release_campaign.promotion_refs, ("pilot-cutover",))
        self.assertEqual(harness.ready_case_ids, ("benchmark-ready",))

    def test_kki_benchmark_harness_runs_recovery_case(self) -> None:
        case = BenchmarkCase(
            case_id="benchmark-recovery",
            title="benchmark recovery",
            missions=(mission_profile_for_name("recovery-drill"),),
            release_mode=BenchmarkReleaseMode.RECOVERY_ONLY,
        )
        harness = run_benchmark_harness((case,), harness_id="harness-148-recovery")

        self.assertEqual(harness.results[0].status, ReleaseCampaignStatus.RECOVERY_ONLY)
        self.assertEqual(harness.results[0].release_campaign.recovery_only_refs, ("recovery-drill",))
        self.assertEqual(harness.recovery_case_ids, ("benchmark-recovery",))

    def test_kki_benchmark_harness_aggregates_matrix_statuses(self) -> None:
        harness = run_benchmark_harness(harness_id="harness-148-matrix")

        self.assertEqual(harness.harness_signal.status, "blocked")
        self.assertEqual(harness.ready_case_ids, ("pilot-ready",))
        self.assertEqual(harness.guarded_case_ids, ("shadow-guarded",))
        self.assertEqual(harness.recovery_case_ids, ("recovery-resume",))
        self.assertEqual(harness.blocked_case_ids, ("pilot-containment",))

    def test_kki_runtime_scorecard_scores_ready_case(self) -> None:
        harness = run_benchmark_harness(
            (
                BenchmarkCase(
                    case_id="scorecard-ready",
                    title="scorecard ready",
                    missions=(mission_profile_for_name("pilot-cutover"),),
                    release_mode=BenchmarkReleaseMode.READY,
                ),
            ),
            harness_id="harness-149-ready",
        )
        scorecard = build_runtime_scorecard(harness, scorecard_id="scorecard-149-ready")

        self.assertIsInstance(scorecard, RuntimeScorecard)
        self.assertIsInstance(scorecard.entries[0], RuntimeScorecardEntry)
        self.assertEqual(scorecard.scorecard_signal.status, "healthy")
        self.assertGreater(scorecard.entries[0].overall_score, 0.8)
        self.assertEqual(scorecard.healthy_case_ids, ("scorecard-ready",))

    def test_kki_runtime_scorecard_marks_guarded_case_for_attention(self) -> None:
        harness = run_benchmark_harness(
            (
                BenchmarkCase(
                    case_id="scorecard-guarded",
                    title="scorecard guarded",
                    missions=(benchmark_case_matrix()[1].missions[0],),
                    release_mode=BenchmarkReleaseMode.GUARDED,
                ),
            ),
            harness_id="harness-149-guarded",
        )
        scorecard = build_runtime_scorecard(harness, scorecard_id="scorecard-149-guarded")

        self.assertEqual(scorecard.scorecard_signal.status, "attention-required")
        self.assertLess(scorecard.entries[0].governance_score, scorecard.entries[0].success_score)
        self.assertEqual(scorecard.attention_case_ids, ("scorecard-guarded",))

    def test_kki_runtime_scorecard_marks_blocked_case_critical(self) -> None:
        harness = run_benchmark_harness(
            (
                BenchmarkCase(
                    case_id="scorecard-blocked",
                    title="scorecard blocked",
                    missions=(mission_profile_for_name("pilot-cutover"),),
                    release_mode=BenchmarkReleaseMode.BLOCKED,
                ),
            ),
            harness_id="harness-149-blocked",
        )
        scorecard = build_runtime_scorecard(harness, scorecard_id="scorecard-149-blocked")

        self.assertEqual(scorecard.scorecard_signal.status, "critical-review")
        self.assertLess(scorecard.entries[0].overall_score, 0.4)
        self.assertEqual(scorecard.attention_case_ids, ("scorecard-blocked",))

    def test_kki_runtime_scorecard_aggregates_matrix_scores(self) -> None:
        scorecard = build_runtime_scorecard(scorecard_id="scorecard-149-matrix")

        self.assertEqual(scorecard.scorecard_signal.status, "critical-review")
        self.assertEqual(scorecard.healthy_case_ids, ("pilot-ready",))
        self.assertEqual(scorecard.attention_case_ids, ("shadow-guarded", "recovery-resume", "pilot-containment"))
        self.assertGreater(scorecard.average_overall_score, 0.4)

    def test_kki_readiness_review_marks_ready_case_release_ready(self) -> None:
        harness = run_benchmark_harness(
            (
                BenchmarkCase(
                    case_id="review-ready",
                    title="review ready",
                    missions=(mission_profile_for_name("pilot-cutover"),),
                    release_mode=BenchmarkReleaseMode.READY,
                ),
            ),
            harness_id="harness-150-ready",
        )
        scorecard = build_runtime_scorecard(harness, scorecard_id="scorecard-150-ready")
        review = build_readiness_review(scorecard, review_id="review-150-ready")

        self.assertIsInstance(review, ReadinessReview)
        self.assertEqual(review.review_signal.status, "ready")
        self.assertTrue(review.release_ready)
        self.assertEqual(review.healthy_case_ids, ("review-ready",))

    def test_kki_readiness_review_routes_guarded_case_to_review(self) -> None:
        harness = run_benchmark_harness(
            (
                BenchmarkCase(
                    case_id="review-guarded",
                    title="review guarded",
                    missions=(benchmark_case_matrix()[1].missions[0],),
                    release_mode=BenchmarkReleaseMode.GUARDED,
                ),
            ),
            harness_id="harness-150-guarded",
        )
        scorecard = build_runtime_scorecard(harness, scorecard_id="scorecard-150-guarded")
        review = build_readiness_review(scorecard, review_id="review-150-guarded")

        self.assertEqual(review.review_signal.status, "review-required")
        self.assertEqual(review.attention_case_ids, ("review-guarded",))
        self.assertTrue(any(finding.severity is ReadinessFindingSeverity.WARNING for finding in review.findings))

    def test_kki_readiness_review_marks_blocked_case_not_ready(self) -> None:
        harness = run_benchmark_harness(
            (
                BenchmarkCase(
                    case_id="review-blocked",
                    title="review blocked",
                    missions=(mission_profile_for_name("pilot-cutover"),),
                    release_mode=BenchmarkReleaseMode.BLOCKED,
                ),
            ),
            harness_id="harness-150-blocked",
        )
        scorecard = build_runtime_scorecard(harness, scorecard_id="scorecard-150-blocked")
        review = build_readiness_review(scorecard, review_id="review-150-blocked")

        self.assertEqual(review.review_signal.status, "not-ready")
        self.assertFalse(review.release_ready)
        self.assertEqual(review.blocked_case_ids, ("review-blocked",))
        self.assertIsInstance(review.findings[0], ReadinessFinding)
        self.assertEqual(review.findings[0].severity, ReadinessFindingSeverity.CRITICAL)

    def test_kki_readiness_review_aggregates_default_chain(self) -> None:
        review = build_readiness_review(review_id="review-150-matrix")

        self.assertEqual(review.review_signal.status, "not-ready")
        self.assertEqual(review.healthy_case_ids, ("pilot-ready",))
        self.assertEqual(review.blocked_case_ids, ("pilot-containment",))
        self.assertFalse(review.release_ready)

    def test_kki_review_action_plan_creates_monitoring_for_ready_case(self) -> None:
        review = build_readiness_review(
            build_runtime_scorecard(
                run_benchmark_harness(
                    (
                        BenchmarkCase(
                            case_id="action-ready",
                            title="action ready",
                            missions=(mission_profile_for_name("pilot-cutover"),),
                            release_mode=BenchmarkReleaseMode.READY,
                        ),
                    ),
                    harness_id="harness-151-ready",
                ),
                scorecard_id="scorecard-151-ready",
            ),
            review_id="review-151-ready",
        )
        plan = build_review_action_plan(review, plan_id="plan-151-ready")

        self.assertIsInstance(plan, ReviewActionPlan)
        self.assertIsInstance(plan.actions[0], ReviewActionItem)
        self.assertEqual(plan.plan_signal.status, "planned")
        self.assertEqual(plan.actions[0].priority, ReviewActionPriority.LOW)
        self.assertEqual(plan.actions[0].action_type, ReviewActionType.MONITOR)

    def test_kki_review_action_plan_routes_governance_findings(self) -> None:
        review = build_readiness_review(
            build_runtime_scorecard(
                run_benchmark_harness(
                    (
                        BenchmarkCase(
                            case_id="action-guarded",
                            title="action guarded",
                            missions=(benchmark_case_matrix()[1].missions[0],),
                            release_mode=BenchmarkReleaseMode.GUARDED,
                        ),
                    ),
                    harness_id="harness-151-guarded",
                ),
                scorecard_id="scorecard-151-guarded",
            ),
            review_id="review-151-guarded",
        )
        plan = build_review_action_plan(review, plan_id="plan-151-guarded")

        self.assertEqual(plan.plan_signal.status, "priority-actions")
        self.assertEqual(plan.actions[0].owner, ModuleBoundaryName.GOVERNANCE)
        self.assertEqual(plan.actions[0].target_status, "governance-reviewed")

    def test_kki_review_action_plan_routes_critical_remediation(self) -> None:
        review = build_readiness_review(
            build_runtime_scorecard(
                run_benchmark_harness(
                    (
                        BenchmarkCase(
                            case_id="action-blocked",
                            title="action blocked",
                            missions=(mission_profile_for_name("pilot-cutover"),),
                            release_mode=BenchmarkReleaseMode.BLOCKED,
                        ),
                    ),
                    harness_id="harness-151-blocked",
                ),
                scorecard_id="scorecard-151-blocked",
            ),
            review_id="review-151-blocked",
        )
        plan = build_review_action_plan(review, plan_id="plan-151-blocked")

        self.assertEqual(plan.plan_signal.status, "critical-actions")
        self.assertEqual(plan.critical_case_ids, ("action-blocked",))
        self.assertEqual(plan.blocked_case_ids, ("action-blocked",))
        self.assertEqual(plan.actions[0].owner, ModuleBoundaryName.RECOVERY)

    def test_kki_review_action_plan_aggregates_default_review(self) -> None:
        plan = build_review_action_plan(plan_id="plan-151-matrix")

        self.assertEqual(plan.plan_signal.status, "critical-actions")
        self.assertEqual(plan.critical_case_ids, ("pilot-containment",))
        self.assertIn(ModuleBoundaryName.GOVERNANCE, plan.owner_boundaries)
        self.assertIn(ModuleBoundaryName.RECOVERY, plan.owner_boundaries)

    def test_kki_risk_register_observes_healthy_case(self) -> None:
        plan = build_review_action_plan(
            build_readiness_review(
                build_runtime_scorecard(
                    run_benchmark_harness(
                        (
                            BenchmarkCase(
                                case_id="risk-ready",
                                title="risk ready",
                                missions=(mission_profile_for_name("pilot-cutover"),),
                                release_mode=BenchmarkReleaseMode.READY,
                            ),
                        ),
                        harness_id="harness-152-ready",
                    ),
                    scorecard_id="scorecard-152-ready",
                ),
                review_id="review-152-ready",
            ),
            plan_id="plan-152-ready",
        )
        register = build_risk_register(plan, register_id="register-152-ready")

        self.assertIsInstance(register, RiskRegister)
        self.assertIsInstance(register.risks[0], RiskRecord)
        self.assertEqual(register.register_signal.status, "observed")
        self.assertEqual(register.risks[0].mitigation_status, RiskMitigationStatus.OBSERVE)
        self.assertEqual(register.risks[0].likelihood, RiskLikelihood.LOW)

    def test_kki_risk_register_tracks_governance_risk(self) -> None:
        plan = build_review_action_plan(plan_id="plan-152-guarded")
        governance_only_plan = ReviewActionPlan(
            plan_id=plan.plan_id,
            review=plan.review,
            actions=(next(action for action in plan.actions if action.case_id == "shadow-guarded"),),
            plan_signal=plan.plan_signal,
            final_snapshot=plan.final_snapshot,
        )
        register = build_risk_register(governance_only_plan, register_id="register-152-guarded")

        self.assertEqual(register.register_signal.status, "active-risks")
        self.assertEqual(register.risks[0].owner, ModuleBoundaryName.GOVERNANCE)
        self.assertEqual(register.risks[0].impact, RiskImpact.HIGH)
        self.assertEqual(register.active_case_ids, ("shadow-guarded",))

    def test_kki_risk_register_tracks_blocking_risk(self) -> None:
        plan = build_review_action_plan(plan_id="plan-152-blocked")
        blocked_only_plan = ReviewActionPlan(
            plan_id=plan.plan_id,
            review=plan.review,
            actions=(next(action for action in plan.actions if action.case_id == "pilot-containment"),),
            plan_signal=plan.plan_signal,
            final_snapshot=plan.final_snapshot,
        )
        register = build_risk_register(blocked_only_plan, register_id="register-152-blocked")

        self.assertEqual(register.register_signal.status, "blocking-risks")
        self.assertEqual(register.blocking_case_ids, ("pilot-containment",))
        self.assertEqual(register.risks[0].impact, RiskImpact.CRITICAL)
        self.assertEqual(register.risks[0].mitigation_status, RiskMitigationStatus.BLOCKING)

    def test_kki_risk_register_aggregates_default_plan(self) -> None:
        register = build_risk_register(register_id="register-152-matrix")

        self.assertEqual(register.register_signal.status, "blocking-risks")
        self.assertIn("pilot-containment", register.blocking_case_ids)
        self.assertIn(ModuleBoundaryName.GOVERNANCE, register.owner_boundaries)
        self.assertIn(ModuleBoundaryName.RECOVERY, register.owner_boundaries)

    def test_kki_guardrail_portfolio_monitors_healthy_case(self) -> None:
        portfolio = build_guardrail_portfolio(
            build_risk_register(
                build_review_action_plan(
                    build_readiness_review(
                        build_runtime_scorecard(
                            run_benchmark_harness(
                                (
                                    BenchmarkCase(
                                        case_id="guardrail-ready",
                                        title="guardrail ready",
                                        missions=(mission_profile_for_name("pilot-cutover"),),
                                        release_mode=BenchmarkReleaseMode.READY,
                                    ),
                                ),
                                harness_id="harness-153-ready",
                            ),
                            scorecard_id="scorecard-153-ready",
                        ),
                        review_id="review-153-ready",
                    ),
                    plan_id="plan-153-ready",
                ),
                register_id="register-153-ready",
            ),
            portfolio_id="portfolio-153-ready",
        )

        self.assertIsInstance(portfolio, GuardrailPortfolio)
        self.assertIsInstance(portfolio.guardrails[0], Guardrail)
        self.assertEqual(portfolio.portfolio_signal.status, "monitoring")
        self.assertEqual(portfolio.guardrails[0].policy_mode, GuardrailPolicyMode.MONITOR)
        self.assertEqual(portfolio.guardrails[0].domain, GuardrailDomain.TELEMETRY)

    def test_kki_guardrail_portfolio_holds_governance_case(self) -> None:
        portfolio = build_guardrail_portfolio(portfolio_id="portfolio-153-guarded")
        governance_guardrail = next(guardrail for guardrail in portfolio.guardrails if guardrail.case_id == "shadow-guarded")

        self.assertEqual(portfolio.portfolio_signal.status, "containment-guardrails")
        self.assertEqual(governance_guardrail.domain, GuardrailDomain.GOVERNANCE)
        self.assertEqual(governance_guardrail.policy_mode, GuardrailPolicyMode.HOLD)

    def test_kki_guardrail_portfolio_contains_blocking_case(self) -> None:
        portfolio = build_guardrail_portfolio(portfolio_id="portfolio-153-blocked")
        blocking_guardrail = next(guardrail for guardrail in portfolio.guardrails if guardrail.case_id == "pilot-containment")

        self.assertEqual(blocking_guardrail.policy_mode, GuardrailPolicyMode.CONTAIN)
        self.assertEqual(blocking_guardrail.domain, GuardrailDomain.RECOVERY)
        self.assertEqual(portfolio.blocking_case_ids, ("pilot-containment",))

    def test_kki_guardrail_portfolio_aggregates_domains(self) -> None:
        portfolio = build_guardrail_portfolio(portfolio_id="portfolio-153-matrix")

        self.assertIn(GuardrailDomain.GOVERNANCE, portfolio.domains)
        self.assertIn(GuardrailDomain.RECOVERY, portfolio.domains)
        self.assertIn(ModuleBoundaryName.GOVERNANCE, portfolio.owner_boundaries)
        self.assertIn(ModuleBoundaryName.RECOVERY, portfolio.owner_boundaries)

    def test_kki_scenario_replay_replays_guarded_case(self) -> None:
        suite = build_scenario_replay(replay_id="replay-154-guarded")
        guarded_item = next(item for item in suite.items if item.source_case_id == "shadow-guarded")

        self.assertIsInstance(suite, ScenarioReplaySuite)
        self.assertIsInstance(guarded_item, ScenarioReplayItem)
        self.assertEqual(guarded_item.replay_mode, ReplayMode.GUARDED)
        self.assertIn("shadow-guarded", suite.replayed_case_ids)

    def test_kki_scenario_replay_contains_blocked_case(self) -> None:
        suite = build_scenario_replay(replay_id="replay-154-blocked")
        blocked_result = next(result for result in suite.results if result.item.source_case_id == "pilot-containment")

        self.assertIsInstance(blocked_result, ScenarioReplayResult)
        self.assertEqual(blocked_result.item.replay_mode, ReplayMode.CONTAINED)
        self.assertEqual(blocked_result.result.status, ReleaseCampaignStatus.BLOCKED)
        self.assertEqual(suite.blocked_case_ids, ("pilot-containment",))

    def test_kki_scenario_replay_can_include_ready_case(self) -> None:
        suite = build_scenario_replay(replay_id="replay-154-ready", include_ready=True)
        ready_result = next(result for result in suite.results if result.item.source_case_id == "pilot-ready")

        self.assertEqual(ready_result.item.replay_mode, ReplayMode.OBSERVED)
        self.assertTrue(ready_result.stable)

    def test_kki_scenario_replay_aggregates_attention_cases(self) -> None:
        suite = build_scenario_replay(replay_id="replay-154-matrix")

        self.assertEqual(suite.replay_signal.status, "blocked-replays")
        self.assertEqual(suite.replayed_case_ids, ("shadow-guarded", "recovery-resume", "pilot-containment"))
        self.assertEqual(suite.blocked_case_ids, ("pilot-containment",))

    def test_kki_drift_monitor_tracks_stable_ready_case(self) -> None:
        replay_suite = build_scenario_replay(replay_id="replay-155-ready", include_ready=True)
        ready_only_suite = ScenarioReplaySuite(
            replay_id=replay_suite.replay_id,
            source_harness=replay_suite.source_harness,
            guardrail_portfolio=replay_suite.guardrail_portfolio,
            items=(next(item for item in replay_suite.items if item.source_case_id == "pilot-ready"),),
            results=(next(result for result in replay_suite.results if result.item.source_case_id == "pilot-ready"),),
            replay_signal=replay_suite.replay_signal,
            final_snapshot=replay_suite.final_snapshot,
        )
        monitor = build_drift_monitor(replay_suite=ready_only_suite, monitor_id="drift-155-ready")
        observation = monitor.observations[0]

        self.assertIsInstance(monitor, DriftMonitor)
        self.assertIsInstance(observation, DriftObservation)
        self.assertTrue(observation.stable)
        self.assertEqual(observation.severity, DriftSeverity.STABLE)

    def test_kki_drift_monitor_detects_governance_violation(self) -> None:
        monitor = build_drift_monitor(monitor_id="drift-155-governance")
        observation = next(item for item in monitor.observations if item.case_id == "shadow-guarded")

        self.assertIn("shadow-guarded", monitor.violating_case_ids)
        self.assertEqual(observation.severity, DriftSeverity.CRITICAL)
        self.assertTrue(any("governance_score" in violation for violation in observation.guardrail_violations))

    def test_kki_drift_monitor_detects_blocked_case_violation(self) -> None:
        monitor = build_drift_monitor(monitor_id="drift-155-blocked")
        observation = next(item for item in monitor.observations if item.case_id == "pilot-containment")

        self.assertEqual(observation.replay_status, ReleaseCampaignStatus.BLOCKED)
        self.assertIn("pilot-containment", monitor.violating_case_ids)
        self.assertEqual(observation.severity, DriftSeverity.CRITICAL)

    def test_kki_drift_monitor_aggregates_recovery_and_governance(self) -> None:
        monitor = build_drift_monitor(monitor_id="drift-155-matrix")

        self.assertEqual(monitor.drift_signal.status, "guardrail-violations")
        self.assertIn("shadow-guarded", monitor.governance_drift_case_ids)
        self.assertIn("pilot-containment", monitor.violating_case_ids)

    def test_kki_improvement_orchestrator_prioritizes_blocked_case(self) -> None:
        orchestrator = build_improvement_orchestrator(orchestrator_id="orchestrator-156-critical")
        blocked_wave = next(wave for wave in orchestrator.waves if wave.case_id == "pilot-containment")

        self.assertIsInstance(orchestrator, ImprovementOrchestrator)
        self.assertIsInstance(blocked_wave, ImprovementWave)
        self.assertEqual(blocked_wave.priority, ImprovementPriority.CRITICAL)
        self.assertEqual(blocked_wave.execution_mode, ImprovementExecutionMode.CONTAINED)
        self.assertIn("pilot-containment", orchestrator.blocked_case_ids)

    def test_kki_improvement_orchestrator_governs_shadow_case(self) -> None:
        orchestrator = build_improvement_orchestrator(orchestrator_id="orchestrator-156-governed")
        governance_wave = next(wave for wave in orchestrator.waves if wave.case_id == "shadow-guarded")

        self.assertEqual(governance_wave.owner, ModuleBoundaryName.GOVERNANCE)
        self.assertEqual(governance_wave.execution_mode, ImprovementExecutionMode.GOVERNED)
        self.assertEqual(governance_wave.priority, ImprovementPriority.HIGH)

    def test_kki_improvement_orchestrator_normalizes_budgets(self) -> None:
        orchestrator = build_improvement_orchestrator(orchestrator_id="orchestrator-156-budget")
        total_budget = sum(wave.budget_share for wave in orchestrator.waves)
        blocked_wave = next(wave for wave in orchestrator.waves if wave.case_id == "pilot-containment")
        healthy_wave = next(wave for wave in orchestrator.waves if wave.case_id == "pilot-ready")

        self.assertAlmostEqual(total_budget, 1.0, places=6)
        self.assertGreater(blocked_wave.budget_share, healthy_wave.budget_share)

    def test_kki_improvement_orchestrator_aggregates_waves(self) -> None:
        orchestrator = build_improvement_orchestrator(orchestrator_id="orchestrator-156-matrix")

        self.assertEqual(orchestrator.orchestration_signal.status, "critical-waves")
        self.assertIn(ModuleBoundaryName.GOVERNANCE, orchestrator.owner_boundaries)
        self.assertIn(ModuleBoundaryName.RECOVERY, orchestrator.owner_boundaries)

    def test_kki_remediation_campaign_contains_blocked_case(self) -> None:
        campaign = build_remediation_campaign(campaign_id="campaign-157-blocked")
        blocked_stage = next(
            stage for stage in campaign.stages if stage.case_id == "pilot-containment" and stage.stage_type is RemediationCampaignStageType.CONTAINMENT
        )

        self.assertIsInstance(campaign, RemediationCampaign)
        self.assertIsInstance(blocked_stage, RemediationCampaignStage)
        self.assertEqual(campaign.status, RemediationCampaignStatus.BLOCKED)
        self.assertEqual(blocked_stage.status, RemediationCampaignStatus.BLOCKED)
        self.assertIn("pilot-containment", campaign.blocked_case_ids)

    def test_kki_remediation_campaign_governs_shadow_case(self) -> None:
        campaign = build_remediation_campaign(campaign_id="campaign-157-governed")
        governance_stage = next(
            stage
            for stage in campaign.stages
            if stage.case_id == "shadow-guarded" and stage.stage_type is RemediationCampaignStageType.GOVERNANCE_APPROVAL
        )

        self.assertEqual(governance_stage.status, RemediationCampaignStatus.GUARDED)
        self.assertTrue(governance_stage.governance_refs)
        self.assertIn("shadow-guarded", campaign.governance_case_ids)

    def test_kki_remediation_campaign_tracks_recovery_case(self) -> None:
        campaign = build_remediation_campaign(campaign_id="campaign-157-recovery")
        recovery_stage = next(
            stage
            for stage in campaign.stages
            if stage.case_id == "recovery-resume" and stage.stage_type is RemediationCampaignStageType.RECOVERY_SAFEGUARD
        )

        self.assertEqual(recovery_stage.status, RemediationCampaignStatus.RECOVERY_ONLY)
        self.assertTrue(recovery_stage.safeguard_refs)
        self.assertIn("recovery-resume", campaign.recovery_case_ids)

    def test_kki_remediation_campaign_aggregates_commitments(self) -> None:
        campaign = build_remediation_campaign(campaign_id="campaign-157-matrix")

        self.assertTrue(campaign.commitment_refs)
        self.assertGreaterEqual(len(campaign.evidence_records), len(campaign.stages))
        self.assertEqual(campaign.campaign_signal.status, "blocked")

    def test_kki_operations_cockpit_tracks_healthy_case(self) -> None:
        cockpit = build_operations_cockpit(cockpit_id="cockpit-158-healthy")
        ready_entry = next(entry for entry in cockpit.entries if entry.case_id == "pilot-ready")

        self.assertIsInstance(cockpit, OperationsCockpit)
        self.assertIsInstance(ready_entry, CockpitEntry)
        self.assertEqual(ready_entry.status, CockpitStatus.HEALTHY)
        self.assertIn("pilot-ready", cockpit.healthy_case_ids)

    def test_kki_operations_cockpit_surfaces_governed_case(self) -> None:
        cockpit = build_operations_cockpit(cockpit_id="cockpit-158-attention")
        guarded_entry = next(entry for entry in cockpit.entries if entry.case_id == "shadow-guarded")

        self.assertEqual(guarded_entry.status, CockpitStatus.ATTENTION)
        self.assertEqual(guarded_entry.remediation_status, RemediationCampaignStatus.GUARDED.value)
        self.assertIn("shadow-guarded", cockpit.attention_case_ids)

    def test_kki_operations_cockpit_surfaces_critical_case(self) -> None:
        cockpit = build_operations_cockpit(cockpit_id="cockpit-158-critical")
        blocked_entry = next(entry for entry in cockpit.entries if entry.case_id == "pilot-containment")

        self.assertEqual(blocked_entry.status, CockpitStatus.CRITICAL)
        self.assertTrue(blocked_entry.blocked_release)
        self.assertIn("pilot-containment", cockpit.critical_case_ids)

    def test_kki_operations_cockpit_aggregates_status_counts(self) -> None:
        cockpit = build_operations_cockpit(cockpit_id="cockpit-158-matrix")

        self.assertEqual(cockpit.cockpit_signal.status, "critical")
        self.assertIn("pilot-ready", cockpit.healthy_case_ids)
        self.assertIn("shadow-guarded", cockpit.attention_case_ids)
        self.assertIn("pilot-containment", cockpit.critical_case_ids)

    def test_kki_portfolio_optimizer_prioritizes_blocked_case(self) -> None:
        optimizer = build_portfolio_optimizer(optimizer_id="optimizer-159-critical")
        blocked_recommendation = next(rec for rec in optimizer.recommendations if rec.case_id == "pilot-containment")

        self.assertIsInstance(optimizer, PortfolioOptimizer)
        self.assertIsInstance(blocked_recommendation, PortfolioRecommendation)
        self.assertEqual(blocked_recommendation.priority, PortfolioPriority.CRITICAL)
        self.assertEqual(blocked_recommendation.action, PortfolioAction.CONTAIN)
        self.assertIn("pilot-containment", optimizer.critical_case_ids)

    def test_kki_portfolio_optimizer_recommends_governance_approval(self) -> None:
        optimizer = build_portfolio_optimizer(optimizer_id="optimizer-159-governed")
        governance_recommendation = next(rec for rec in optimizer.recommendations if rec.case_id == "shadow-guarded")

        self.assertEqual(governance_recommendation.priority, PortfolioPriority.HIGH)
        self.assertEqual(governance_recommendation.action, PortfolioAction.APPROVE)
        self.assertEqual(governance_recommendation.owner, ModuleBoundaryName.GOVERNANCE)

    def test_kki_portfolio_optimizer_recommends_release_candidate(self) -> None:
        optimizer = build_portfolio_optimizer(optimizer_id="optimizer-159-release")
        ready_recommendation = next(rec for rec in optimizer.recommendations if rec.case_id == "pilot-ready")

        self.assertEqual(ready_recommendation.action, PortfolioAction.ADVANCE)
        self.assertTrue(ready_recommendation.release_candidate)
        self.assertIn("pilot-ready", optimizer.release_candidate_ids)

    def test_kki_portfolio_optimizer_aggregates_priority_queue(self) -> None:
        optimizer = build_portfolio_optimizer(optimizer_id="optimizer-159-matrix")

        self.assertEqual(optimizer.optimizer_signal.status, "critical-priorities")
        self.assertEqual(optimizer.recommendations[0].case_id, "pilot-containment")
        self.assertGreaterEqual(optimizer.recommendations[0].net_value, 0.0)

    def test_kki_continuous_readiness_marks_release_candidate_ready(self) -> None:
        cycle = build_continuous_readiness_cycle(cycle_id="cycle-160-ready")
        ready_iteration = next(iteration for iteration in cycle.iterations if iteration.case_id == "pilot-ready")

        self.assertIsInstance(cycle, ContinuousReadinessCycle)
        self.assertIsInstance(ready_iteration, ContinuousReadinessIteration)
        self.assertEqual(ready_iteration.status, ContinuousReadinessStatus.READY)
        self.assertTrue(ready_iteration.release_candidate)

    def test_kki_continuous_readiness_marks_governed_case_attention(self) -> None:
        cycle = build_continuous_readiness_cycle(cycle_id="cycle-160-governed")
        governed_iteration = next(iteration for iteration in cycle.iterations if iteration.case_id == "shadow-guarded")

        self.assertEqual(governed_iteration.status, ContinuousReadinessStatus.ATTENTION)
        self.assertEqual(governed_iteration.next_review_status, "review-required")
        self.assertIn("shadow-guarded", cycle.attention_case_ids)

    def test_kki_continuous_readiness_marks_blocked_case_not_ready(self) -> None:
        cycle = build_continuous_readiness_cycle(cycle_id="cycle-160-blocked")
        blocked_iteration = next(iteration for iteration in cycle.iterations if iteration.case_id == "pilot-containment")

        self.assertEqual(blocked_iteration.status, ContinuousReadinessStatus.BLOCKED)
        self.assertEqual(blocked_iteration.next_review_status, "not-ready")
        self.assertIn("pilot-containment", cycle.blocked_case_ids)

    def test_kki_continuous_readiness_aggregates_focus_cases(self) -> None:
        cycle = build_continuous_readiness_cycle(cycle_id="cycle-160-matrix")

        self.assertEqual(cycle.cycle_signal.status, "blocked")
        self.assertIn("pilot-ready", cycle.ready_case_ids)
        self.assertIn("shadow-guarded", cycle.next_focus_case_ids)
        self.assertIn("pilot-containment", cycle.blocked_case_ids)

    def test_kki_readiness_cadence_schedules_blocked_case_immediately(self) -> None:
        cadence = build_readiness_cadence(cadence_id="cadence-161-blocked")
        blocked_entry = next(entry for entry in cadence.entries if entry.case_id == "pilot-containment")

        self.assertIsInstance(cadence, ReadinessCadence)
        self.assertIsInstance(blocked_entry, ReadinessCadenceEntry)
        self.assertEqual(blocked_entry.trigger, ReadinessCadenceTrigger.CONTAINMENT)
        self.assertEqual(blocked_entry.window, ReadinessCadenceWindow.IMMEDIATE)
        self.assertEqual(blocked_entry.cadence_status, ReadinessCadenceStatus.ESCALATED)
        self.assertEqual(blocked_entry.due_cycle, 1)

    def test_kki_readiness_cadence_schedules_governed_case_in_current_window(self) -> None:
        cadence = build_readiness_cadence(cadence_id="cadence-161-governed")
        governed_entry = next(entry for entry in cadence.entries if entry.case_id == "shadow-guarded")

        self.assertEqual(governed_entry.trigger, ReadinessCadenceTrigger.GOVERNANCE)
        self.assertEqual(governed_entry.window, ReadinessCadenceWindow.CURRENT)
        self.assertEqual(governed_entry.cadence_status, ReadinessCadenceStatus.REVIEW_REQUIRED)
        self.assertIn("shadow-guarded", cadence.current_window_case_ids)

    def test_kki_readiness_cadence_schedules_release_candidate_in_next_window(self) -> None:
        cadence = build_readiness_cadence(cadence_id="cadence-161-release")
        ready_entry = next(entry for entry in cadence.entries if entry.case_id == "pilot-ready")

        self.assertEqual(ready_entry.trigger, ReadinessCadenceTrigger.PROMOTION)
        self.assertEqual(ready_entry.window, ReadinessCadenceWindow.NEXT)
        self.assertEqual(ready_entry.cadence_status, ReadinessCadenceStatus.STEADY)
        self.assertTrue(ready_entry.release_candidate)
        self.assertIn("pilot-ready", cadence.next_window_case_ids)

    def test_kki_readiness_cadence_aggregates_focus_metrics(self) -> None:
        cadence = build_readiness_cadence(cadence_id="cadence-161-matrix")

        self.assertEqual(cadence.cadence_signal.status, "escalated")
        self.assertIn("pilot-containment", cadence.immediate_case_ids)
        self.assertIn("shadow-guarded", cadence.focus_case_ids)
        self.assertIn("pilot-ready", cadence.next_window_case_ids)

    def test_kki_escalation_router_routes_blocked_case_to_recovery(self) -> None:
        router = build_escalation_router(router_id="router-162-blocked")
        blocked_route = next(route for route in router.routes if route.case_id == "pilot-containment")

        self.assertIsInstance(router, EscalationRouter)
        self.assertIsInstance(blocked_route, EscalationRoute)
        self.assertEqual(blocked_route.path, EscalationRoutePath.RECOVERY_CONTAINMENT)
        self.assertEqual(blocked_route.boundary, ModuleBoundaryName.RECOVERY)
        self.assertTrue(blocked_route.release_blocked)
        self.assertIn("pilot-containment", router.recovery_case_ids)

    def test_kki_escalation_router_routes_governed_case_to_governance(self) -> None:
        router = build_escalation_router(router_id="router-162-governed")
        governed_route = next(route for route in router.routes if route.case_id == "shadow-guarded")

        self.assertEqual(governed_route.path, EscalationRoutePath.GOVERNANCE_REVIEW)
        self.assertEqual(governed_route.boundary, ModuleBoundaryName.GOVERNANCE)
        self.assertIn("shadow-guarded", router.governance_case_ids)

    def test_kki_escalation_router_routes_steady_case_to_telemetry(self) -> None:
        router = build_escalation_router(router_id="router-162-steady")
        steady_route = next(route for route in router.routes if route.case_id == "pilot-ready")

        self.assertEqual(steady_route.path, EscalationRoutePath.TELEMETRY_WATCH)
        self.assertEqual(steady_route.boundary, ModuleBoundaryName.TELEMETRY)
        self.assertFalse(steady_route.release_blocked)
        self.assertIn("pilot-ready", router.telemetry_case_ids)

    def test_kki_escalation_router_aggregates_focus_routes(self) -> None:
        router = build_escalation_router(router_id="router-162-matrix")

        self.assertEqual(router.router_signal.status, "critical-response")
        self.assertIn("pilot-containment", router.blocked_case_ids)
        self.assertIn("shadow-guarded", router.focus_case_ids)
        self.assertIn("pilot-ready", router.telemetry_case_ids)

    def test_kki_evidence_ledger_collects_review_evidence(self) -> None:
        ledger = build_evidence_ledger(ledger_id="ledger-163-review")
        review_entry = next(
            entry
            for entry in ledger.entries
            if entry.case_id == "shadow-guarded" and entry.source is EvidenceLedgerSource.REVIEW
        )

        self.assertIsInstance(ledger, EvidenceLedger)
        self.assertIsInstance(review_entry, EvidenceLedgerEntry)
        self.assertEqual(review_entry.route_path, EscalationRoutePath.GOVERNANCE_REVIEW)
        self.assertEqual(review_entry.boundary, ModuleBoundaryName.GOVERNANCE)
        self.assertEqual(review_entry.evidence_record.evidence_type, "readiness-review-finding")

    def test_kki_evidence_ledger_collects_replay_evidence(self) -> None:
        ledger = build_evidence_ledger(ledger_id="ledger-163-replay")
        replay_entry = next(
            entry
            for entry in ledger.entries
            if entry.case_id == "pilot-containment" and entry.source is EvidenceLedgerSource.REPLAY
        )

        self.assertEqual(replay_entry.route_path, EscalationRoutePath.RECOVERY_CONTAINMENT)
        self.assertEqual(replay_entry.evidence_record.evidence_type, "scenario-replay-result")
        self.assertEqual(replay_entry.cycle_index, 1)

    def test_kki_evidence_ledger_collects_remediation_commitments(self) -> None:
        ledger = build_evidence_ledger(ledger_id="ledger-163-remediation")
        remediation_entry = next(
            entry
            for entry in ledger.entries
            if entry.case_id == "pilot-containment" and entry.source is EvidenceLedgerSource.REMEDIATION
        )

        self.assertTrue(remediation_entry.commitment_refs)
        self.assertTrue(remediation_entry.evidence_record.commitment_ref)
        self.assertIn(remediation_entry.commitment_refs[0], ledger.commitment_refs)

    def test_kki_evidence_ledger_aggregates_case_tracks(self) -> None:
        ledger = build_evidence_ledger(ledger_id="ledger-163-matrix")

        self.assertEqual(ledger.ledger_signal.status, "blocked-evidence")
        self.assertIn("pilot-containment", ledger.blocked_case_ids)
        self.assertIn("shadow-guarded", ledger.governance_case_ids)
        self.assertIn("pilot-containment", ledger.recovery_case_ids)

    def test_kki_capacity_planner_admits_blocked_case_immediately(self) -> None:
        planner = build_capacity_planner(planner_id="planner-164-blocked")
        blocked_entry = next(entry for entry in planner.entries if entry.case_id == "pilot-containment")

        self.assertIsInstance(planner, CapacityPlanner)
        self.assertIsInstance(blocked_entry, CapacityPlanEntry)
        self.assertEqual(blocked_entry.window, CapacityWindow.IMMEDIATE)
        self.assertEqual(blocked_entry.lane, CapacityLane.ADMIT)
        self.assertEqual(blocked_entry.wip_slot, 1)

    def test_kki_capacity_planner_admits_governance_case_current_window(self) -> None:
        planner = build_capacity_planner(planner_id="planner-164-governance")
        governed_entry = next(entry for entry in planner.entries if entry.case_id == "shadow-guarded")

        self.assertEqual(governed_entry.window, CapacityWindow.CURRENT)
        self.assertEqual(governed_entry.lane, CapacityLane.ADMIT)
        self.assertIn("shadow-guarded", planner.current_window_case_ids)

    def test_kki_capacity_planner_defers_release_candidate_to_next_window(self) -> None:
        planner = build_capacity_planner(planner_id="planner-164-release")
        ready_entry = next(entry for entry in planner.entries if entry.case_id == "pilot-ready")

        self.assertEqual(ready_entry.window, CapacityWindow.NEXT)
        self.assertEqual(ready_entry.lane, CapacityLane.DEFER)
        self.assertTrue(ready_entry.release_candidate)
        self.assertIn("pilot-ready", planner.deferred_case_ids)

    def test_kki_capacity_planner_aggregates_budget_and_wip(self) -> None:
        planner = build_capacity_planner(planner_id="planner-164-matrix")

        self.assertEqual(planner.planner_signal.status, "immediate-capacity")
        self.assertEqual(planner.admitted_case_ids[:2], ("pilot-containment", "shadow-guarded"))
        self.assertLessEqual(planner.consumed_budget, planner.total_budget)
        self.assertIn("pilot-containment", planner.immediate_case_ids)

    def test_kki_governance_agenda_schedules_governance_case(self) -> None:
        agenda = build_governance_agenda(agenda_id="agenda-165-governed")
        governed_item = next(item for item in agenda.items if item.case_id == "shadow-guarded")

        self.assertIsInstance(agenda, GovernanceAgenda)
        self.assertIsInstance(governed_item, GovernanceAgendaItem)
        self.assertEqual(governed_item.agenda_status, GovernanceAgendaStatus.SCHEDULED)
        self.assertEqual(governed_item.decision, HumanDecision.APPROVE)
        self.assertIn("shadow-guarded", agenda.scheduled_case_ids)

    def test_kki_governance_agenda_tracks_governance_evidence(self) -> None:
        agenda = build_governance_agenda(agenda_id="agenda-165-evidence")
        governed_item = next(item for item in agenda.items if item.case_id == "shadow-guarded")

        self.assertTrue(governed_item.evidence_refs)
        self.assertEqual(governed_item.route_path, EscalationRoutePath.GOVERNANCE_REVIEW)

    def test_kki_governance_agenda_excludes_non_governance_cases(self) -> None:
        agenda = build_governance_agenda(agenda_id="agenda-165-scope")

        self.assertNotIn("pilot-containment", [item.case_id for item in agenda.items])
        self.assertNotIn("pilot-ready", [item.case_id for item in agenda.items])

    def test_kki_governance_agenda_aggregates_queue_state(self) -> None:
        agenda = build_governance_agenda(agenda_id="agenda-165-matrix")

        self.assertEqual(agenda.agenda_signal.status, "scheduled")
        self.assertEqual(agenda.scheduled_case_ids, ("shadow-guarded",))
        self.assertFalse(agenda.blocked_case_ids)

    def test_kki_recovery_drills_schedule_blocked_case(self) -> None:
        drills = build_recovery_drill_suite(suite_id="drills-166-blocked")
        blocked_drill = next(drill for drill in drills.drills if drill.case_id == "pilot-containment")

        self.assertIsInstance(drills, RecoveryDrillSuite)
        self.assertIsInstance(blocked_drill, RecoveryDrill)
        self.assertEqual(blocked_drill.mode, RecoveryMode.ROLLBACK)
        self.assertEqual(blocked_drill.disposition, RecoveryDisposition.CONTAIN)

    def test_kki_recovery_drills_mark_active_blocked_case(self) -> None:
        drills = build_recovery_drill_suite(suite_id="drills-166-active")
        blocked_drill = next(drill for drill in drills.drills if drill.case_id == "pilot-containment")

        self.assertEqual(blocked_drill.status, RecoveryDrillStatus.ACTIVE)
        self.assertIn("pilot-containment", drills.active_case_ids)

    def test_kki_recovery_drills_capture_reentry_conditions(self) -> None:
        drills = build_recovery_drill_suite(suite_id="drills-166-conditions")
        blocked_drill = next(drill for drill in drills.drills if drill.case_id == "pilot-containment")

        self.assertIn("replay-evidence-updated", blocked_drill.reentry_conditions)
        self.assertIn("remediation-commitments-complete", blocked_drill.reentry_conditions)
        self.assertIn("readiness-review-revalidated", blocked_drill.reentry_conditions)

    def test_kki_recovery_drills_aggregate_suite_status(self) -> None:
        drills = build_recovery_drill_suite(suite_id="drills-166-matrix")

        self.assertEqual(drills.drill_signal.status, "active")
        self.assertEqual(drills.active_case_ids, ("pilot-containment",))
        self.assertFalse(drills.reentry_ready_case_ids)

    def test_kki_convergence_simulator_projects_three_cycles(self) -> None:
        simulator = build_convergence_simulator(simulator_id="convergence-167-cycles")

        self.assertIsInstance(simulator, ConvergenceSimulator)
        self.assertEqual(len(simulator.projections), 3)
        self.assertTrue(all(isinstance(projection, ConvergenceProjection) for projection in simulator.projections))
        self.assertEqual(
            tuple(projection.status for projection in simulator.projections),
            (
                ConvergenceStatus.RESIDUAL_DRIFT,
                ConvergenceStatus.STABILIZING,
                ConvergenceStatus.CONVERGED,
            ),
        )

    def test_kki_convergence_simulator_reduces_residual_drift(self) -> None:
        simulator = build_convergence_simulator(simulator_id="convergence-167-drift")
        drifts = tuple(projection.residual_drift for projection in simulator.projections)

        self.assertGreater(drifts[0], drifts[1])
        self.assertGreater(drifts[1], drifts[2])
        self.assertEqual(drifts[-1], 0.0)

    def test_kki_convergence_simulator_recovers_cases_by_final_cycle(self) -> None:
        simulator = build_convergence_simulator(simulator_id="convergence-167-ready")

        self.assertEqual(simulator.projections[0].blocked_case_ids, ("pilot-containment",))
        self.assertEqual(
            simulator.final_ready_case_ids,
            ("pilot-containment", "shadow-guarded", "recovery-resume", "pilot-ready"),
        )
        self.assertFalse(simulator.residual_case_ids)

    def test_kki_convergence_simulator_aggregates_converged_signal(self) -> None:
        simulator = build_convergence_simulator(simulator_id="convergence-167-signal")

        self.assertEqual(simulator.simulator_signal.status, "converged")
        self.assertEqual(simulator.converged_cycle_index, 3)
        self.assertEqual(simulator.projections[-1].recovery_case_ids, ("pilot-containment",))

    def test_kki_policy_tuner_tightens_recovery_paths(self) -> None:
        tuner = build_policy_tuner(tuner_id="policy-168-recovery")
        containment_entry = next(entry for entry in tuner.entries if entry.case_id == "pilot-containment")
        restart_entry = next(entry for entry in tuner.entries if entry.case_id == "recovery-resume")

        self.assertIsInstance(tuner, PolicyTuner)
        self.assertIsInstance(containment_entry, PolicyTuneEntry)
        self.assertEqual(containment_entry.action, PolicyTuneAction.TIGHTEN)
        self.assertEqual(containment_entry.tuned_policy_mode, GuardrailPolicyMode.CONTAIN)
        self.assertEqual(restart_entry.tuned_policy_mode, GuardrailPolicyMode.HOLD)

    def test_kki_policy_tuner_calibrates_governance_policy(self) -> None:
        tuner = build_policy_tuner(tuner_id="policy-168-governance")
        governed_entry = next(entry for entry in tuner.entries if entry.case_id == "shadow-guarded")

        self.assertEqual(governed_entry.action, PolicyTuneAction.CALIBRATE)
        self.assertEqual(governed_entry.route_path, EscalationRoutePath.GOVERNANCE_REVIEW)
        self.assertGreater(governed_entry.tuned_threshold, governed_entry.current_threshold)

    def test_kki_policy_tuner_relaxes_stable_telemetry_case(self) -> None:
        tuner = build_policy_tuner(tuner_id="policy-168-telemetry")
        telemetry_entry = next(entry for entry in tuner.entries if entry.case_id == "pilot-ready")

        self.assertEqual(telemetry_entry.action, PolicyTuneAction.RELAX)
        self.assertEqual(telemetry_entry.tuned_policy_mode, GuardrailPolicyMode.MONITOR)
        self.assertLess(telemetry_entry.tuned_threshold, telemetry_entry.current_threshold)

    def test_kki_policy_tuner_aggregates_adjustment_signal(self) -> None:
        tuner = build_policy_tuner(tuner_id="policy-168-signal")

        self.assertEqual(tuner.tuner_signal.status, "policy-tightening")
        self.assertEqual(tuner.tightened_case_ids, ("recovery-resume", "pilot-containment"))
        self.assertEqual(tuner.calibrated_case_ids, ("shadow-guarded",))
        self.assertEqual(tuner.relaxed_case_ids, ("pilot-ready",))

    def test_kki_learning_register_captures_interventions(self) -> None:
        register = build_learning_register(register_id="learning-169-interventions")
        intervention = next(record for record in register.records if record.case_id == "pilot-containment")

        self.assertIsInstance(register, LearningRegister)
        self.assertIsInstance(intervention, LearningRecord)
        self.assertEqual(intervention.pattern_type, LearningPatternType.STABILIZED_INTERVENTION)
        self.assertEqual(intervention.source_action, PolicyTuneAction.TIGHTEN)
        self.assertTrue(intervention.evidence_refs)
        self.assertTrue(intervention.commitment_refs)

    def test_kki_learning_register_captures_operating_recipe(self) -> None:
        register = build_learning_register(register_id="learning-169-recipe")
        recipe = next(record for record in register.records if record.case_id == "shadow-guarded")

        self.assertEqual(recipe.pattern_type, LearningPatternType.OPERATING_RECIPE)
        self.assertEqual(recipe.route_path, EscalationRoutePath.GOVERNANCE_REVIEW)
        self.assertTrue(recipe.reusable)

    def test_kki_learning_register_captures_recurring_pattern(self) -> None:
        register = build_learning_register(register_id="learning-169-pattern")
        pattern = next(record for record in register.records if record.case_id == "pilot-ready")

        self.assertEqual(pattern.pattern_type, LearningPatternType.RECURRING_PATTERN)
        self.assertEqual(pattern.source_action, PolicyTuneAction.RELAX)
        self.assertGreater(pattern.confidence_score, 0.7)

    def test_kki_learning_register_aggregates_reusable_knowledge(self) -> None:
        register = build_learning_register(register_id="learning-169-signal")

        self.assertEqual(register.register_signal.status, "reusable-learning")
        self.assertEqual(register.intervention_case_ids, ("recovery-resume", "pilot-containment"))
        self.assertEqual(register.recipe_case_ids, ("shadow-guarded",))
        self.assertEqual(register.recurring_pattern_case_ids, ("pilot-ready",))
        self.assertEqual(register.reusable_case_ids, ("shadow-guarded", "recovery-resume", "pilot-containment", "pilot-ready"))

    def test_kki_operations_steward_stabilizes_blocked_case(self) -> None:
        steward = build_operations_steward(steward_id="steward-170-stabilize")
        directive = next(item for item in steward.directives if item.case_id == "pilot-containment")

        self.assertIsInstance(steward, OperationsSteward)
        self.assertIsInstance(directive, StewardDirective)
        self.assertEqual(directive.directive_type, StewardDirectiveType.STABILIZE)
        self.assertEqual(directive.policy_action, PolicyTuneAction.TIGHTEN)
        self.assertEqual(directive.learning_pattern, LearningPatternType.STABILIZED_INTERVENTION)

    def test_kki_operations_steward_governs_review_case(self) -> None:
        steward = build_operations_steward(steward_id="steward-170-govern")
        directive = next(item for item in steward.directives if item.case_id == "shadow-guarded")

        self.assertEqual(directive.directive_type, StewardDirectiveType.GOVERN)
        self.assertEqual(directive.route_path, EscalationRoutePath.GOVERNANCE_REVIEW)
        self.assertTrue(directive.evidence_refs)

    def test_kki_operations_steward_adapts_remaining_cases(self) -> None:
        steward = build_operations_steward(steward_id="steward-170-adapt")

        self.assertEqual(steward.adapt_case_ids, ("recovery-resume",))
        self.assertEqual(steward.monitor_case_ids, ("pilot-ready",))
        self.assertEqual(steward.govern_case_ids, ("shadow-guarded",))

    def test_kki_operations_steward_aggregates_control_signal(self) -> None:
        steward = build_operations_steward(steward_id="steward-170-signal")

        self.assertEqual(steward.steward_signal.status, OperationsStewardStatus.CRITICAL.value)
        self.assertEqual(steward.stabilize_case_ids, ("pilot-containment",))
        self.assertAlmostEqual(steward.steward_signal.metrics["directive_count"], 4.0)

    def test_kki_steward_workboard_expedites_blocked_case(self) -> None:
        workboard = build_steward_workboard(workboard_id="workboard-171-expedite")
        item = next(item for item in workboard.items if item.case_id == "pilot-containment")

        self.assertIsInstance(workboard, StewardWorkboard)
        self.assertIsInstance(item, WorkboardItem)
        self.assertEqual(item.queue, WorkboardQueue.STABILIZATION)
        self.assertEqual(item.lane, WorkboardLane.EXPEDITE)
        self.assertEqual(item.status, WorkboardStatus.DUE_NOW)

    def test_kki_steward_workboard_tracks_governance_case(self) -> None:
        workboard = build_steward_workboard(workboard_id="workboard-171-governance")
        item = next(item for item in workboard.items if item.case_id == "shadow-guarded")

        self.assertEqual(item.queue, WorkboardQueue.GOVERNANCE)
        self.assertEqual(item.lane, WorkboardLane.COMMITTED)
        self.assertEqual(item.sla_hours, 12)

    def test_kki_steward_workboard_places_follow_up_and_watch_items(self) -> None:
        workboard = build_steward_workboard(workboard_id="workboard-171-lanes")

        self.assertEqual(workboard.follow_up_case_ids, ("recovery-resume",))
        self.assertEqual(workboard.watch_case_ids, ("pilot-ready",))
        self.assertEqual(workboard.committed_case_ids, ("shadow-guarded",))

    def test_kki_steward_workboard_aggregates_board_signal(self) -> None:
        workboard = build_steward_workboard(workboard_id="workboard-171-signal")

        self.assertEqual(workboard.board_signal.status, "expedite-board")
        self.assertEqual(workboard.expedite_case_ids, ("pilot-containment",))
        self.assertEqual(workboard.due_now_case_ids, ("pilot-containment",))
        self.assertAlmostEqual(workboard.board_signal.metrics["item_count"], 4.0)

    def test_kki_outcome_ledger_tracks_contained_case(self) -> None:
        ledger = build_outcome_ledger(ledger_id="outcome-172-contained")
        record = next(item for item in ledger.records if item.case_id == "pilot-containment")

        self.assertIsInstance(ledger, OutcomeLedger)
        self.assertIsInstance(record, OutcomeRecord)
        self.assertEqual(record.outcome_status, OutcomeStatus.CONTAINED)
        self.assertTrue(record.resolved_within_sla)
        self.assertTrue(record.exception_candidate)

    def test_kki_outcome_ledger_tracks_governed_case(self) -> None:
        ledger = build_outcome_ledger(ledger_id="outcome-172-governed")
        record = next(item for item in ledger.records if item.case_id == "shadow-guarded")

        self.assertEqual(record.outcome_status, OutcomeStatus.GOVERNED)
        self.assertTrue(record.outcome_ref.startswith("outcome-"))
        self.assertTrue(record.evidence_refs)

    def test_kki_outcome_ledger_tracks_tuned_and_observed_cases(self) -> None:
        ledger = build_outcome_ledger(ledger_id="outcome-172-mix")

        self.assertEqual(ledger.tuned_case_ids, ("recovery-resume",))
        self.assertEqual(ledger.observed_case_ids, ("pilot-ready",))
        self.assertEqual(ledger.exception_candidate_case_ids, ("pilot-containment", "recovery-resume"))

    def test_kki_outcome_ledger_aggregates_execution_signal(self) -> None:
        ledger = build_outcome_ledger(ledger_id="outcome-172-signal")

        self.assertEqual(ledger.ledger_signal.status, "stabilizing-outcomes")
        self.assertEqual(ledger.contained_case_ids, ("pilot-containment",))
        self.assertEqual(ledger.governed_case_ids, ("shadow-guarded",))
        self.assertAlmostEqual(ledger.ledger_signal.metrics["record_count"], 4.0)

    def test_kki_exception_register_tracks_policy_breach_case(self) -> None:
        register = build_exception_register(register_id="exception-173-breach")
        case = next(item for item in register.exceptions if item.case_id == "pilot-containment")

        self.assertIsInstance(register, ExceptionRegister)
        self.assertIsInstance(case, ExceptionCase)
        self.assertEqual(case.kind, ExceptionKind.POLICY_BREACH)
        self.assertEqual(case.severity, ExceptionSeverity.CRITICAL)

    def test_kki_exception_register_tracks_unresolved_case(self) -> None:
        register = build_exception_register(register_id="exception-173-unresolved")
        case = next(item for item in register.exceptions if item.case_id == "recovery-resume")

        self.assertEqual(case.kind, ExceptionKind.UNRESOLVED)
        self.assertEqual(case.severity, ExceptionSeverity.HIGH)
        self.assertIn("unresolved", case.escalation_reason)

    def test_kki_exception_register_excludes_routine_cases(self) -> None:
        register = build_exception_register(register_id="exception-173-scope")

        self.assertNotIn("shadow-guarded", [item.case_id for item in register.exceptions])
        self.assertNotIn("pilot-ready", [item.case_id for item in register.exceptions])

    def test_kki_exception_register_aggregates_exception_signal(self) -> None:
        register = build_exception_register(register_id="exception-173-signal")

        self.assertEqual(register.register_signal.status, "critical-exceptions")
        self.assertEqual(register.critical_case_ids, ("pilot-containment",))
        self.assertEqual(register.unresolved_case_ids, ("recovery-resume",))
        self.assertEqual(register.policy_breach_case_ids, ("pilot-containment",))

    def test_kki_playbook_catalog_compiles_steward_guided_playbooks(self) -> None:
        catalog = build_playbook_catalog(catalog_id="playbook-174-guided")
        playbook = next(item for item in catalog.playbooks if item.case_id == "pilot-containment")

        self.assertIsInstance(catalog, PlaybookCatalog)
        self.assertIsInstance(playbook, PlaybookEntry)
        self.assertEqual(playbook.playbook_type, PlaybookType.STABILIZATION)
        self.assertEqual(playbook.readiness, PlaybookReadiness.STEWARD_GUIDED)

    def test_kki_playbook_catalog_compiles_governed_standard_playbooks(self) -> None:
        catalog = build_playbook_catalog(catalog_id="playbook-174-governed")
        playbook = next(item for item in catalog.playbooks if item.case_id == "shadow-guarded")

        self.assertEqual(playbook.playbook_type, PlaybookType.GOVERNANCE)
        self.assertEqual(playbook.readiness, PlaybookReadiness.GOVERNED_STANDARD)
        self.assertFalse(playbook.automation_candidate)

    def test_kki_playbook_catalog_marks_autonomy_candidates(self) -> None:
        catalog = build_playbook_catalog(catalog_id="playbook-174-autonomy")
        playbook = next(item for item in catalog.playbooks if item.case_id == "pilot-ready")

        self.assertEqual(playbook.playbook_type, PlaybookType.MONITORING)
        self.assertEqual(playbook.readiness, PlaybookReadiness.AUTONOMY_CANDIDATE)
        self.assertIn("Eligible for controlled autonomous execution.", playbook.steps)

    def test_kki_playbook_catalog_aggregates_catalog_signal(self) -> None:
        catalog = build_playbook_catalog(catalog_id="playbook-174-signal")

        self.assertEqual(catalog.catalog_signal.status, "catalog-autonomy-ready")
        self.assertEqual(catalog.steward_guided_case_ids, ("pilot-containment", "recovery-resume"))
        self.assertEqual(catalog.governed_case_ids, ("shadow-guarded",))
        self.assertEqual(catalog.autonomy_candidate_case_ids, ("pilot-ready",))

    def test_kki_autonomy_governor_enables_bounded_autonomy(self) -> None:
        governor = build_autonomy_governor(governor_id="autonomy-175-auto")
        assignment = next(item for item in governor.assignments if item.case_id == "pilot-ready")

        self.assertIsInstance(governor, AutonomyGovernor)
        self.assertIsInstance(assignment, AutonomyAssignment)
        self.assertEqual(assignment.decision, AutonomyDecision.AUTONOMOUS)
        self.assertTrue(assignment.automation_allowed)

    def test_kki_autonomy_governor_requires_governance_for_standard_case(self) -> None:
        governor = build_autonomy_governor(governor_id="autonomy-175-governance")
        assignment = next(item for item in governor.assignments if item.case_id == "shadow-guarded")

        self.assertEqual(assignment.decision, AutonomyDecision.GOVERNANCE_REQUIRED)
        self.assertTrue(assignment.governance_required)
        self.assertIn("approval-gate", assignment.control_tags)

    def test_kki_autonomy_governor_keeps_exception_cases_with_steward(self) -> None:
        governor = build_autonomy_governor(governor_id="autonomy-175-steward")

        self.assertEqual(governor.steward_required_case_ids, ("pilot-containment", "recovery-resume"))
        self.assertIn("exception-escalation", next(item for item in governor.assignments if item.case_id == "pilot-containment").control_tags)

    def test_kki_autonomy_governor_aggregates_governor_signal(self) -> None:
        governor = build_autonomy_governor(governor_id="autonomy-175-signal")

        self.assertEqual(governor.governor_signal.status, "autonomy-enabled")
        self.assertEqual(governor.autonomous_case_ids, ("pilot-ready",))
        self.assertEqual(governor.governance_required_case_ids, ("shadow-guarded",))
        self.assertAlmostEqual(governor.governor_signal.metrics["assignment_count"], 4.0)

    def test_kki_intervention_simulator_projects_ready_autonomous_case(self) -> None:
        simulator = build_intervention_simulator(simulator_id="intervention-176-ready")
        simulation = next(item for item in simulator.simulations if item.case_id == "pilot-ready")

        self.assertIsInstance(simulator, InterventionSimulator)
        self.assertIsInstance(simulation, InterventionSimulation)
        self.assertEqual(simulation.intervention_mode, InterventionMode.AUTONOMOUS)
        self.assertEqual(simulation.projected_status, InterventionSimulationStatus.READY)
        self.assertEqual(simulation.fallback_path, InterventionFallback.OBSERVE_ONLY)

    def test_kki_intervention_simulator_projects_guarded_governance_case(self) -> None:
        simulator = build_intervention_simulator(simulator_id="intervention-176-guarded")
        simulation = next(item for item in simulator.simulations if item.case_id == "shadow-guarded")

        self.assertEqual(simulation.intervention_mode, InterventionMode.GOVERNED)
        self.assertEqual(simulation.projected_status, InterventionSimulationStatus.GUARDED)
        self.assertEqual(simulation.fallback_path, InterventionFallback.APPROVAL_GATE)

    def test_kki_intervention_simulator_flags_risk_and_rollback_cases(self) -> None:
        simulator = build_intervention_simulator(simulator_id="intervention-176-risk")

        rollback_case = next(item for item in simulator.simulations if item.case_id == "pilot-containment")
        at_risk_case = next(item for item in simulator.simulations if item.case_id == "recovery-resume")
        self.assertEqual(rollback_case.projected_status, InterventionSimulationStatus.ROLLBACK_RECOMMENDED)
        self.assertEqual(rollback_case.fallback_path, InterventionFallback.ROLLBACK)
        self.assertEqual(at_risk_case.projected_status, InterventionSimulationStatus.AT_RISK)
        self.assertTrue(at_risk_case.regression_risk)

    def test_kki_intervention_simulator_aggregates_simulation_signal(self) -> None:
        simulator = build_intervention_simulator(simulator_id="intervention-176-signal")

        self.assertEqual(simulator.simulator_signal.status, "rollback-recommended")
        self.assertEqual(simulator.ready_case_ids, ("pilot-ready",))
        self.assertEqual(simulator.guarded_case_ids, ("shadow-guarded",))
        self.assertEqual(simulator.at_risk_case_ids, ("recovery-resume",))
        self.assertEqual(simulator.rollback_case_ids, ("pilot-containment",))

    def test_kki_federation_coordination_builds_resilience_cell(self) -> None:
        coordination = build_federation_coordination(coordination_id="federation-177-resilience")
        cell = next(item for item in coordination.cells if item.domain is FederationDomain.RESILIENCE)

        self.assertIsInstance(coordination, FederationCoordination)
        self.assertIsInstance(cell, FederationCell)
        self.assertEqual(cell.alignment_status, FederationAlignmentStatus.ESCALATED)
        self.assertEqual(cell.case_ids, ("pilot-containment", "recovery-resume"))

    def test_kki_federation_coordination_builds_governance_and_autonomy_cells(self) -> None:
        coordination = build_federation_coordination(coordination_id="federation-177-domains")

        governance_cell = next(item for item in coordination.cells if item.domain is FederationDomain.GOVERNANCE)
        autonomy_cell = next(item for item in coordination.cells if item.domain is FederationDomain.AUTONOMY)
        self.assertEqual(governance_cell.alignment_status, FederationAlignmentStatus.HANDOFF_REQUIRED)
        self.assertEqual(governance_cell.case_ids, ("shadow-guarded",))
        self.assertEqual(autonomy_cell.alignment_status, FederationAlignmentStatus.ALIGNED)
        self.assertEqual(autonomy_cell.case_ids, ("pilot-ready",))

    def test_kki_federation_coordination_creates_domain_handoffs(self) -> None:
        coordination = build_federation_coordination(coordination_id="federation-177-handoffs")

        self.assertEqual(len(coordination.handoffs), 2)
        self.assertIsInstance(coordination.handoffs[0], FederationHandoff)
        self.assertEqual(coordination.handoffs[0].priority, FederationHandoffPriority.CRITICAL)
        self.assertEqual(coordination.handoffs[1].priority, FederationHandoffPriority.PLANNED)

    def test_kki_federation_coordination_aggregates_coordination_signal(self) -> None:
        coordination = build_federation_coordination(coordination_id="federation-177-signal")

        self.assertEqual(coordination.coordination_signal.status, "federated-escalation")
        self.assertEqual(coordination.escalated_domains, (FederationDomain.RESILIENCE,))
        self.assertEqual(coordination.handoff_domains, (FederationDomain.GOVERNANCE,))
        self.assertEqual(coordination.aligned_domains, (FederationDomain.AUTONOMY,))

    def test_kki_program_controller_builds_resilience_track(self) -> None:
        controller = build_program_controller(controller_id="program-178-resilience")
        track = next(item for item in controller.tracks if item.track_type is ProgramTrackType.RESILIENCE)

        self.assertIsInstance(controller, ProgramController)
        self.assertIsInstance(track, ProgramTrack)
        self.assertEqual(track.directive, ProgramDirective.INTERVENE)
        self.assertEqual(track.status, ProgramControllerStatus.CRITICAL)

    def test_kki_program_controller_builds_governance_track(self) -> None:
        controller = build_program_controller(controller_id="program-178-governance")
        track = next(item for item in controller.tracks if item.track_type is ProgramTrackType.GOVERNANCE)

        self.assertEqual(track.case_ids, ("shadow-guarded",))
        self.assertEqual(track.directive, ProgramDirective.STEER)
        self.assertEqual(track.status, ProgramControllerStatus.CONTROLLED)

    def test_kki_program_controller_builds_routine_scaling_track(self) -> None:
        controller = build_program_controller(controller_id="program-178-routine")
        track = next(item for item in controller.tracks if item.track_type is ProgramTrackType.ROUTINE)

        self.assertEqual(track.case_ids, ("pilot-ready",))
        self.assertEqual(track.directive, ProgramDirective.SCALE)
        self.assertEqual(track.status, ProgramControllerStatus.SCALING)

    def test_kki_program_controller_aggregates_program_signal(self) -> None:
        controller = build_program_controller(controller_id="program-178-signal")

        self.assertEqual(controller.controller_signal.status, "program-critical")
        self.assertEqual(controller.critical_track_ids, ("program-178-signal-resilience",))
        self.assertEqual(controller.controlled_track_ids, ("program-178-signal-governance",))
        self.assertEqual(controller.scaling_track_ids, ("program-178-signal-autonomy",))

    def test_kki_operating_constitution_builds_steward_article(self) -> None:
        constitution = build_operating_constitution(constitution_id="constitution-179-steward")
        article = next(item for item in constitution.articles if item.authority is ConstitutionalAuthority.STEWARD)

        self.assertIsInstance(constitution, OperatingConstitution)
        self.assertIsInstance(article, ConstitutionArticle)
        self.assertEqual(article.principle, ConstitutionPrinciple.STABILITY_FIRST)
        self.assertEqual(article.case_ids, ("pilot-containment", "recovery-resume"))

    def test_kki_operating_constitution_builds_governance_article(self) -> None:
        constitution = build_operating_constitution(constitution_id="constitution-179-governance")
        article = next(item for item in constitution.articles if item.authority is ConstitutionalAuthority.GOVERNANCE)

        self.assertEqual(article.principle, ConstitutionPrinciple.GOVERNED_CHANGE)
        self.assertEqual(article.budget_ceiling, 0.65)
        self.assertEqual(article.escalation_limit, 2)

    def test_kki_operating_constitution_builds_bounded_autonomy_article(self) -> None:
        constitution = build_operating_constitution(constitution_id="constitution-179-autonomy")
        article = next(item for item in constitution.articles if item.authority is ConstitutionalAuthority.AUTONOMY)

        self.assertEqual(article.principle, ConstitutionPrinciple.BOUNDED_AUTONOMY)
        self.assertIn("bounded-execution", article.execution_rights)
        self.assertEqual(article.escalation_limit, 3)

    def test_kki_operating_constitution_aggregates_constitution_signal(self) -> None:
        constitution = build_operating_constitution(constitution_id="constitution-179-signal")

        self.assertEqual(constitution.constitution_signal.status, "bounded-autonomy-chartered")
        self.assertEqual(constitution.steward_article_ids, ("constitution-179-signal-resilience-program",))
        self.assertEqual(constitution.governance_article_ids, ("constitution-179-signal-governance-program",))
        self.assertEqual(constitution.autonomy_article_ids, ("constitution-179-signal-routine-program",))

    def test_kki_executive_watchtower_builds_locked_resilience_order(self) -> None:
        watchtower = build_executive_watchtower(watchtower_id="executive-180-resilience")
        order = next(item for item in watchtower.orders if item.track_type is ProgramTrackType.RESILIENCE)

        self.assertIsInstance(watchtower, ExecutiveWatchtower)
        self.assertIsInstance(order, ExecutiveOrder)
        self.assertEqual(order.mode, ExecutiveOrderMode.EXECUTIVE_OVERRIDE)
        self.assertEqual(order.watch_status, ExecutiveWatchStatus.LOCKED)

    def test_kki_executive_watchtower_builds_commanding_governance_order(self) -> None:
        watchtower = build_executive_watchtower(watchtower_id="executive-180-governance")
        order = next(item for item in watchtower.orders if item.track_type is ProgramTrackType.GOVERNANCE)

        self.assertEqual(order.mode, ExecutiveOrderMode.GOVERNED_EXECUTION)
        self.assertEqual(order.watch_status, ExecutiveWatchStatus.COMMANDING)
        self.assertFalse(order.release_ready)

    def test_kki_executive_watchtower_builds_ready_autonomy_order(self) -> None:
        watchtower = build_executive_watchtower(watchtower_id="executive-180-autonomy")
        order = next(item for item in watchtower.orders if item.track_type is ProgramTrackType.ROUTINE)

        self.assertEqual(order.mode, ExecutiveOrderMode.AUTONOMY_WINDOW)
        self.assertEqual(order.watch_status, ExecutiveWatchStatus.READY)
        self.assertTrue(order.release_ready)

    def test_kki_executive_watchtower_aggregates_watchtower_signal(self) -> None:
        watchtower = build_executive_watchtower(watchtower_id="executive-180-signal")

        self.assertEqual(watchtower.watchtower_signal.status, "executive-locked")
        self.assertEqual(watchtower.locked_order_ids, ("executive-180-signal-resilience-program",))
        self.assertEqual(watchtower.commanding_order_ids, ("executive-180-signal-governance-program",))
        self.assertEqual(watchtower.ready_order_ids, ("executive-180-signal-routine-program",))

    def test_kki_strategy_council_builds_escalated_stability_mandate(self) -> None:
        council = build_strategy_council(council_id="strategy-181-resilience")
        mandate = next(item for item in council.mandates if item.lane is StrategyLane.STABILITY)

        self.assertIsInstance(council, StrategyCouncil)
        self.assertIsInstance(mandate, StrategyMandate)
        self.assertEqual(mandate.priority, StrategyPriority.IMMEDIATE)
        self.assertEqual(mandate.escalation_mandate, StrategyEscalationMandate.CONTAINMENT)
        self.assertEqual(mandate.council_status, StrategyCouncilStatus.ESCALATED)

    def test_kki_strategy_council_builds_orchestrated_governance_mandate(self) -> None:
        council = build_strategy_council(council_id="strategy-181-governance")
        mandate = next(item for item in council.mandates if item.lane is StrategyLane.GOVERNANCE)

        self.assertEqual(mandate.priority, StrategyPriority.DIRECTED)
        self.assertEqual(mandate.escalation_mandate, StrategyEscalationMandate.REVIEW)
        self.assertEqual(mandate.council_status, StrategyCouncilStatus.ORCHESTRATED)
        self.assertFalse(mandate.release_ready)

    def test_kki_strategy_council_builds_primed_expansion_mandate(self) -> None:
        council = build_strategy_council(council_id="strategy-181-expansion")
        mandate = next(item for item in council.mandates if item.lane is StrategyLane.EXPANSION)

        self.assertEqual(mandate.priority, StrategyPriority.COMPOUND)
        self.assertEqual(mandate.escalation_mandate, StrategyEscalationMandate.EXPANSION)
        self.assertEqual(mandate.council_status, StrategyCouncilStatus.PRIMED)
        self.assertTrue(mandate.release_ready)

    def test_kki_strategy_council_aggregates_council_signal(self) -> None:
        council = build_strategy_council(council_id="strategy-181-signal")

        self.assertEqual(council.council_signal.status, "strategy-escalated")
        self.assertEqual(council.escalated_mandate_ids, ("strategy-181-signal-stability-lane",))
        self.assertEqual(council.orchestrated_mandate_ids, ("strategy-181-signal-governance-lane",))
        self.assertEqual(council.primed_mandate_ids, ("strategy-181-signal-expansion-lane",))

    def test_kki_mandate_card_deck_builds_steward_containment_card(self) -> None:
        deck = build_mandate_card_deck(deck_id="mandate-182-steward")
        card = next(item for item in deck.cards if item.owner is ConstitutionalAuthority.STEWARD)

        self.assertIsInstance(deck, MandateCardDeck)
        self.assertIsInstance(card, MandateCard)
        self.assertEqual(card.execution_scope, MandateExecutionScope.CONTAINMENT)
        self.assertEqual(card.review_cadence, MandateReviewCadence.INCIDENT)

    def test_kki_mandate_card_deck_builds_governance_review_card(self) -> None:
        deck = build_mandate_card_deck(deck_id="mandate-182-governance")
        card = next(item for item in deck.cards if item.owner is ConstitutionalAuthority.GOVERNANCE)

        self.assertEqual(card.execution_scope, MandateExecutionScope.GOVERNED_CHANGE)
        self.assertEqual(card.review_cadence, MandateReviewCadence.GOVERNANCE)
        self.assertFalse(card.release_ready)

    def test_kki_mandate_card_deck_builds_autonomy_expansion_card(self) -> None:
        deck = build_mandate_card_deck(deck_id="mandate-182-autonomy")
        card = next(item for item in deck.cards if item.owner is ConstitutionalAuthority.AUTONOMY)

        self.assertEqual(card.execution_scope, MandateExecutionScope.BOUNDED_EXPANSION)
        self.assertEqual(card.review_cadence, MandateReviewCadence.EXPANSION)
        self.assertTrue(card.release_ready)

    def test_kki_mandate_card_deck_aggregates_deck_signal(self) -> None:
        deck = build_mandate_card_deck(deck_id="mandate-182-signal")

        self.assertEqual(deck.deck_signal.status, "mandate-containment-owned")
        self.assertEqual(deck.steward_card_ids, ("mandate-182-signal-stability-lane",))
        self.assertEqual(deck.governance_card_ids, ("mandate-182-signal-governance-lane",))
        self.assertEqual(deck.autonomy_card_ids, ("mandate-182-signal-expansion-lane",))

    def test_kki_portfolio_radar_builds_concentrated_stability_entry(self) -> None:
        radar = build_portfolio_radar(radar_id="portfolio-183-stability")
        entry = next(item for item in radar.entries if item.exposure is PortfolioExposure.CONTAINED)

        self.assertIsInstance(radar, PortfolioRadar)
        self.assertIsInstance(entry, PortfolioRadarEntry)
        self.assertEqual(entry.concentration, PortfolioConcentration.CONCENTRATED)
        self.assertEqual(entry.operating_spread, PortfolioOperatingSpread.NARROW)

    def test_kki_portfolio_radar_builds_governed_balanced_entry(self) -> None:
        radar = build_portfolio_radar(radar_id="portfolio-183-governance")
        entry = next(item for item in radar.entries if item.exposure is PortfolioExposure.GOVERNED)

        self.assertEqual(entry.concentration, PortfolioConcentration.BALANCED)
        self.assertEqual(entry.operating_spread, PortfolioOperatingSpread.COORDINATED)
        self.assertFalse(entry.release_ready)

    def test_kki_portfolio_radar_builds_expansive_distributed_entry(self) -> None:
        radar = build_portfolio_radar(radar_id="portfolio-183-expansion")
        entry = next(item for item in radar.entries if item.exposure is PortfolioExposure.EXPANSIVE)

        self.assertEqual(entry.concentration, PortfolioConcentration.DISTRIBUTED)
        self.assertEqual(entry.operating_spread, PortfolioOperatingSpread.BROAD)
        self.assertTrue(entry.release_ready)

    def test_kki_portfolio_radar_aggregates_radar_signal(self) -> None:
        radar = build_portfolio_radar(radar_id="portfolio-183-signal")

        self.assertEqual(radar.radar_signal.status, "portfolio-concentrated")
        self.assertEqual(radar.concentrated_entry_ids, ("portfolio-183-signal-stability-lane",))
        self.assertEqual(radar.governed_entry_ids, ("portfolio-183-signal-governance-lane",))
        self.assertEqual(radar.expansive_entry_ids, ("portfolio-183-signal-expansion-lane",))

    def test_kki_scenario_chancery_builds_locked_stabilize_option(self) -> None:
        chancery = build_scenario_chancery(chancery_id="scenario-184-stability")
        option = next(item for item in chancery.options if item.mode is ScenarioOfficeMode.STABILIZE)

        self.assertIsInstance(chancery, ScenarioChancery)
        self.assertIsInstance(option, ScenarioOption)
        self.assertEqual(option.status, ScenarioOfficeStatus.LOCKED)
        self.assertFalse(option.release_ready)

    def test_kki_scenario_chancery_builds_review_steer_option(self) -> None:
        chancery = build_scenario_chancery(chancery_id="scenario-184-governance")
        option = next(item for item in chancery.options if item.mode is ScenarioOfficeMode.STEER)

        self.assertEqual(option.status, ScenarioOfficeStatus.REVIEW)
        self.assertGreater(option.comparison_score, 0.7)
        self.assertFalse(option.release_ready)

    def test_kki_scenario_chancery_builds_ready_expand_option(self) -> None:
        chancery = build_scenario_chancery(chancery_id="scenario-184-expansion")
        option = next(item for item in chancery.options if item.mode is ScenarioOfficeMode.EXPAND)

        self.assertEqual(option.status, ScenarioOfficeStatus.READY)
        self.assertTrue(option.release_ready)
        self.assertGreater(option.confidence_score, 0.6)

    def test_kki_scenario_chancery_aggregates_chancery_signal(self) -> None:
        chancery = build_scenario_chancery(chancery_id="scenario-184-signal")

        self.assertEqual(chancery.chancery_signal.status, "scenario-locked")
        self.assertEqual(chancery.locked_option_ids, ("scenario-184-signal-stability-lane",))
        self.assertEqual(chancery.review_option_ids, ("scenario-184-signal-governance-lane",))
        self.assertEqual(chancery.ready_option_ids, ("scenario-184-signal-expansion-lane",))

    def test_kki_course_corrector_builds_enforced_contain_directive(self) -> None:
        corrector = build_course_corrector(corrector_id="course-185-stability")
        directive = next(item for item in corrector.directives if item.action is CourseCorrectionAction.CONTAIN)

        self.assertIsInstance(corrector, CourseCorrector)
        self.assertIsInstance(directive, CourseCorrectionDirective)
        self.assertEqual(directive.status, CourseCorrectionStatus.ENFORCED)
        self.assertFalse(directive.release_ready)

    def test_kki_course_corrector_builds_directed_rebalance_directive(self) -> None:
        corrector = build_course_corrector(corrector_id="course-185-governance")
        directive = next(item for item in corrector.directives if item.action is CourseCorrectionAction.REBALANCE)

        self.assertEqual(directive.status, CourseCorrectionStatus.DIRECTED)
        self.assertGreater(directive.correction_score, 0.7)
        self.assertFalse(directive.release_ready)

    def test_kki_course_corrector_builds_cleared_accelerate_directive(self) -> None:
        corrector = build_course_corrector(corrector_id="course-185-expansion")
        directive = next(item for item in corrector.directives if item.action is CourseCorrectionAction.ACCELERATE)

        self.assertEqual(directive.status, CourseCorrectionStatus.CLEARED)
        self.assertTrue(directive.release_ready)
        self.assertGreater(directive.stress_index, 0.2)

    def test_kki_course_corrector_aggregates_corrector_signal(self) -> None:
        corrector = build_course_corrector(corrector_id="course-185-signal")

        self.assertEqual(corrector.corrector_signal.status, "course-enforced")
        self.assertEqual(corrector.enforced_directive_ids, ("course-185-signal-stability-lane",))
        self.assertEqual(corrector.directed_directive_ids, ("course-185-signal-governance-lane",))
        self.assertEqual(corrector.cleared_directive_ids, ("course-185-signal-expansion-lane",))

    def test_kki_mandate_memory_store_builds_sealed_record(self) -> None:
        store = build_mandate_memory_store(store_id="memory-186-sealed")
        record = next(item for item in store.records if item.memory_status is MandateMemoryStatus.SEALED)

        self.assertIsInstance(store, MandateMemoryStore)
        self.assertIsInstance(record, MandateMemoryRecord)
        self.assertEqual(record.source_action, CourseCorrectionAction.CONTAIN)
        self.assertFalse(record.release_ready)

    def test_kki_mandate_memory_store_builds_review_record(self) -> None:
        store = build_mandate_memory_store(store_id="memory-186-review")
        record = next(item for item in store.records if item.memory_status is MandateMemoryStatus.REVIEW)

        self.assertEqual(record.source_action, CourseCorrectionAction.REBALANCE)
        self.assertGreater(record.retention_score, 0.7)
        self.assertEqual(record.renewal_window, 4)

    def test_kki_mandate_memory_store_builds_renewable_record(self) -> None:
        store = build_mandate_memory_store(store_id="memory-186-renewable")
        record = next(item for item in store.records if item.memory_status is MandateMemoryStatus.RENEWABLE)

        self.assertEqual(record.source_action, CourseCorrectionAction.ACCELERATE)
        self.assertTrue(record.release_ready)
        self.assertEqual(record.renewal_window, 7)

    def test_kki_mandate_memory_store_aggregates_store_signal(self) -> None:
        store = build_mandate_memory_store(store_id="memory-186-signal")

        self.assertEqual(store.store_signal.status, "memory-sealed")
        self.assertEqual(store.sealed_record_ids, ("memory-186-signal-stability-lane",))
        self.assertEqual(store.review_record_ids, ("memory-186-signal-governance-lane",))
        self.assertEqual(store.renewable_record_ids, ("memory-186-signal-expansion-lane",))

    def test_kki_guideline_compass_builds_anchored_stability_vector(self) -> None:
        compass = build_guideline_compass(compass_id="compass-187-stability")
        vector = next(item for item in compass.vectors if item.compass_status is CompassStatus.ANCHORED)

        self.assertIsInstance(compass, GuidelineCompass)
        self.assertIsInstance(vector, GuidelineVector)
        self.assertEqual(vector.principle, GuidelinePrinciple.STABILITY_FIRST)
        self.assertEqual(vector.navigation_constraint, NavigationConstraint.HARD_BOUNDARY)

    def test_kki_guideline_compass_builds_guided_progress_vector(self) -> None:
        compass = build_guideline_compass(compass_id="compass-187-governance")
        vector = next(item for item in compass.vectors if item.compass_status is CompassStatus.GUIDED)

        self.assertEqual(vector.principle, GuidelinePrinciple.GOVERNED_PROGRESS)
        self.assertEqual(vector.navigation_constraint, NavigationConstraint.GOVERNED_CORRIDOR)
        self.assertGreater(vector.guidance_score, 0.7)

    def test_kki_guideline_compass_builds_open_expansion_vector(self) -> None:
        compass = build_guideline_compass(compass_id="compass-187-expansion")
        vector = next(item for item in compass.vectors if item.compass_status is CompassStatus.OPEN)

        self.assertEqual(vector.principle, GuidelinePrinciple.BOUNDED_EXPANSION)
        self.assertEqual(vector.navigation_constraint, NavigationConstraint.EXPANSION_WINDOW)
        self.assertTrue(vector.release_ready)

    def test_kki_guideline_compass_aggregates_compass_signal(self) -> None:
        compass = build_guideline_compass(compass_id="compass-187-signal")

        self.assertEqual(compass.compass_signal.status, "compass-anchored")
        self.assertEqual(compass.anchored_vector_ids, ("compass-187-signal-stability-lane",))
        self.assertEqual(compass.guided_vector_ids, ("compass-187-signal-governance-lane",))
        self.assertEqual(compass.open_vector_ids, ("compass-187-signal-expansion-lane",))

    def test_kki_intervention_charter_builds_restricted_stability_clause(self) -> None:
        charter = build_intervention_charter(charter_id="charter-188-stability")
        clause = next(item for item in charter.clauses if item.charter_status is CharterStatus.RESTRICTED)

        self.assertIsInstance(charter, InterventionCharter)
        self.assertIsInstance(clause, InterventionClause)
        self.assertEqual(clause.intervention_right, InterventionRight.STEWARD_VETO)
        self.assertEqual(clause.stop_condition, StopCondition.HARD_BOUNDARY_BREACH)
        self.assertEqual(clause.release_threshold, ReleaseThreshold.EXECUTIVE_OVERRIDE)

    def test_kki_intervention_charter_builds_guarded_governance_clause(self) -> None:
        charter = build_intervention_charter(charter_id="charter-188-governance")
        clause = next(item for item in charter.clauses if item.charter_status is CharterStatus.GUARDED)

        self.assertEqual(clause.intervention_right, InterventionRight.GOVERNANCE_REVIEW)
        self.assertEqual(clause.stop_condition, StopCondition.CORRIDOR_DEVIATION)
        self.assertEqual(clause.release_threshold, ReleaseThreshold.GOVERNANCE_CLEARANCE)
        self.assertGreater(clause.intervention_score, 0.7)

    def test_kki_intervention_charter_builds_enabled_expansion_clause(self) -> None:
        charter = build_intervention_charter(charter_id="charter-188-expansion")
        clause = next(item for item in charter.clauses if item.charter_status is CharterStatus.ENABLED)

        self.assertEqual(clause.intervention_right, InterventionRight.AUTONOMY_WINDOW)
        self.assertEqual(clause.stop_condition, StopCondition.WINDOW_EXHAUSTED)
        self.assertEqual(clause.release_threshold, ReleaseThreshold.READINESS_QUORUM)
        self.assertTrue(clause.release_ready)

    def test_kki_intervention_charter_aggregates_charter_signal(self) -> None:
        charter = build_intervention_charter(charter_id="charter-188-signal")

        self.assertEqual(charter.charter_signal.status, "charter-restricted")
        self.assertEqual(charter.restricted_clause_ids, ("charter-188-signal-stability-lane",))
        self.assertEqual(charter.guarded_clause_ids, ("charter-188-signal-governance-lane",))
        self.assertEqual(charter.enabled_clause_ids, ("charter-188-signal-expansion-lane",))

    def test_kki_program_senate_builds_contested_stability_seat(self) -> None:
        senate = build_program_senate(senate_id="senate-189-stability")
        seat = next(item for item in senate.seats if item.balance_status is SenateBalanceStatus.CONTESTED)

        self.assertIsInstance(senate, ProgramSenate)
        self.assertIsInstance(seat, SenateSeat)
        self.assertEqual(seat.priority, SenatePriority.CONSTITUTION_FIRST)
        self.assertEqual(seat.resolution, SenateResolution.VETO)

    def test_kki_program_senate_builds_balanced_governance_seat(self) -> None:
        senate = build_program_senate(senate_id="senate-189-governance")
        seat = next(item for item in senate.seats if item.balance_status is SenateBalanceStatus.BALANCED)

        self.assertEqual(seat.priority, SenatePriority.JOINT_REVIEW)
        self.assertEqual(seat.resolution, SenateResolution.NEGOTIATE)
        self.assertGreater(seat.consensus_score, 0.5)

    def test_kki_program_senate_builds_aligned_expansion_seat(self) -> None:
        senate = build_program_senate(senate_id="senate-189-expansion")
        seat = next(item for item in senate.seats if item.balance_status is SenateBalanceStatus.ALIGNED)

        self.assertEqual(seat.priority, SenatePriority.PROGRAM_ADVANCE)
        self.assertEqual(seat.resolution, SenateResolution.ENDORSE)
        self.assertTrue(seat.release_ready)

    def test_kki_program_senate_aggregates_senate_signal(self) -> None:
        senate = build_program_senate(senate_id="senate-189-signal")

        self.assertEqual(senate.senate_signal.status, "senate-contested")
        self.assertEqual(senate.contested_seat_ids, ("senate-189-signal-stability-lane",))
        self.assertEqual(senate.balanced_seat_ids, ("senate-189-signal-governance-lane",))
        self.assertEqual(senate.aligned_seat_ids, ("senate-189-signal-expansion-lane",))

    def test_kki_directive_consensus_builds_binding_stability_directive(self) -> None:
        consensus = build_directive_consensus(consensus_id="consensus-190-stability")
        directive = next(item for item in consensus.directives if item.directive_status is ConsensusDirectiveStatus.BINDING)

        self.assertIsInstance(consensus, DirectiveConsensus)
        self.assertIsInstance(directive, ConsensusDirective)
        self.assertEqual(directive.directive_type, ConsensusDirectiveType.CONSTITUTIONAL_LOCK)
        self.assertEqual(directive.mandate, ConsensusMandate.HOLD)

    def test_kki_directive_consensus_builds_negotiated_governance_directive(self) -> None:
        consensus = build_directive_consensus(consensus_id="consensus-190-governance")
        directive = next(item for item in consensus.directives if item.directive_status is ConsensusDirectiveStatus.NEGOTIATED)

        self.assertEqual(directive.directive_type, ConsensusDirectiveType.GOVERNED_COMPACT)
        self.assertEqual(directive.mandate, ConsensusMandate.ALIGN)
        self.assertGreater(directive.consensus_strength, 0.5)

    def test_kki_directive_consensus_builds_ratified_expansion_directive(self) -> None:
        consensus = build_directive_consensus(consensus_id="consensus-190-expansion")
        directive = next(item for item in consensus.directives if item.directive_status is ConsensusDirectiveStatus.RATIFIED)

        self.assertEqual(directive.directive_type, ConsensusDirectiveType.EXPANSION_ACCORD)
        self.assertEqual(directive.mandate, ConsensusMandate.RELEASE)
        self.assertTrue(directive.release_ready)

    def test_kki_directive_consensus_aggregates_consensus_signal(self) -> None:
        consensus = build_directive_consensus(consensus_id="consensus-190-signal")

        self.assertEqual(consensus.consensus_signal.status, "consensus-binding")
        self.assertEqual(consensus.binding_directive_ids, ("consensus-190-signal-stability-lane",))
        self.assertEqual(consensus.negotiated_directive_ids, ("consensus-190-signal-governance-lane",))
        self.assertEqual(consensus.ratified_directive_ids, ("consensus-190-signal-expansion-lane",))

    def test_kki_decision_archive_builds_sealed_binding_entry(self) -> None:
        archive = build_decision_archive(archive_id="archive-191-binding")
        entry = next(item for item in archive.entries if item.archive_status is ArchiveStatus.SEALED)

        self.assertIsInstance(archive, DecisionArchive)
        self.assertIsInstance(entry, ArchiveEntry)
        self.assertEqual(entry.retention, ArchiveRetention.AUDIT)
        self.assertEqual(entry.directive_status, ConsensusDirectiveStatus.BINDING)

    def test_kki_decision_archive_builds_indexed_negotiated_entry(self) -> None:
        archive = build_decision_archive(archive_id="archive-191-negotiated")
        entry = next(item for item in archive.entries if item.archive_status is ArchiveStatus.INDEXED)

        self.assertEqual(entry.retention, ArchiveRetention.AUDIT)
        self.assertEqual(entry.directive_status, ConsensusDirectiveStatus.NEGOTIATED)
        self.assertGreater(entry.archive_weight, 0.5)

    def test_kki_decision_archive_builds_codified_ratified_entry(self) -> None:
        archive = build_decision_archive(archive_id="archive-191-ratified")
        entry = next(item for item in archive.entries if item.archive_status is ArchiveStatus.CODIFIED)

        self.assertEqual(entry.retention, ArchiveRetention.KNOWLEDGE)
        self.assertEqual(entry.directive_status, ConsensusDirectiveStatus.RATIFIED)
        self.assertTrue(entry.release_ready)

    def test_kki_decision_archive_aggregates_archive_signal(self) -> None:
        archive = build_decision_archive(archive_id="archive-191-signal")

        self.assertEqual(archive.archive_signal.status, "archive-sealed")
        self.assertEqual(archive.sealed_entry_ids, ("archive-191-signal-stability-lane",))
        self.assertEqual(archive.indexed_entry_ids, ("archive-191-signal-governance-lane",))
        self.assertEqual(archive.codified_entry_ids, ("archive-191-signal-expansion-lane",))

    def test_kki_execution_cabinet_builds_locked_stability_order(self) -> None:
        cabinet = build_execution_cabinet(cabinet_id="cabinet-192-stability")
        order = next(item for item in cabinet.orders if item.cabinet_status is CabinetStatus.LOCKED)

        self.assertIsInstance(cabinet, ExecutionCabinet)
        self.assertIsInstance(order, CabinetOrder)
        self.assertEqual(order.cabinet_role, CabinetRole.STEWARD_CHIEF)
        self.assertEqual(order.execution_mode, CabinetExecutionMode.ENFORCE_HOLD)

    def test_kki_execution_cabinet_builds_supervising_governance_order(self) -> None:
        cabinet = build_execution_cabinet(cabinet_id="cabinet-192-governance")
        order = next(item for item in cabinet.orders if item.cabinet_status is CabinetStatus.SUPERVISING)

        self.assertEqual(order.cabinet_role, CabinetRole.GOVERNANCE_MINISTER)
        self.assertEqual(order.execution_mode, CabinetExecutionMode.COORDINATE_ALIGNMENT)
        self.assertGreater(order.authority_band, 0.6)

    def test_kki_execution_cabinet_builds_commissioned_expansion_order(self) -> None:
        cabinet = build_execution_cabinet(cabinet_id="cabinet-192-expansion")
        order = next(item for item in cabinet.orders if item.cabinet_status is CabinetStatus.COMMISSIONED)

        self.assertEqual(order.cabinet_role, CabinetRole.AUTONOMY_MINISTER)
        self.assertEqual(order.execution_mode, CabinetExecutionMode.AUTHORIZE_RELEASE)
        self.assertTrue(order.release_ready)

    def test_kki_execution_cabinet_aggregates_cabinet_signal(self) -> None:
        cabinet = build_execution_cabinet(cabinet_id="cabinet-192-signal")

        self.assertEqual(cabinet.cabinet_signal.status, "cabinet-locked")
        self.assertEqual(cabinet.locked_order_ids, ("cabinet-192-signal-stability-lane",))
        self.assertEqual(cabinet.supervising_order_ids, ("cabinet-192-signal-governance-lane",))
        self.assertEqual(cabinet.commissioned_order_ids, ("cabinet-192-signal-expansion-lane",))

    def test_kki_delegation_matrix_builds_pinned_steward_entry(self) -> None:
        matrix = build_delegation_matrix(matrix_id="matrix-193-stability")
        entry = next(item for item in matrix.delegations if item.delegation_status is DelegationStatus.PINNED)

        self.assertIsInstance(matrix, DelegationMatrix)
        self.assertIsInstance(entry, DelegationEntry)
        self.assertEqual(entry.delegation_lane, DelegationLane.STEWARD_PATH)
        self.assertEqual(entry.delegation_mode, DelegationMode.HARD_HANDOFF)

    def test_kki_delegation_matrix_builds_routed_governance_entry(self) -> None:
        matrix = build_delegation_matrix(matrix_id="matrix-193-governance")
        entry = next(item for item in matrix.delegations if item.delegation_status is DelegationStatus.ROUTED)

        self.assertEqual(entry.delegation_lane, DelegationLane.GOVERNANCE_PATH)
        self.assertEqual(entry.delegation_mode, DelegationMode.GOVERNED_HANDOFF)
        self.assertGreater(entry.handoff_score, 0.6)

    def test_kki_delegation_matrix_builds_open_autonomy_entry(self) -> None:
        matrix = build_delegation_matrix(matrix_id="matrix-193-expansion")
        entry = next(item for item in matrix.delegations if item.delegation_status is DelegationStatus.OPEN)

        self.assertEqual(entry.delegation_lane, DelegationLane.AUTONOMY_PATH)
        self.assertEqual(entry.delegation_mode, DelegationMode.ENABLED_HANDOFF)
        self.assertTrue(entry.release_ready)

    def test_kki_delegation_matrix_aggregates_matrix_signal(self) -> None:
        matrix = build_delegation_matrix(matrix_id="matrix-193-signal")

        self.assertEqual(matrix.matrix_signal.status, "delegation-pinned")
        self.assertEqual(matrix.pinned_delegation_ids, ("matrix-193-signal-stability-lane",))
        self.assertEqual(matrix.routed_delegation_ids, ("matrix-193-signal-governance-lane",))
        self.assertEqual(matrix.open_delegation_ids, ("matrix-193-signal-expansion-lane",))

    def test_kki_veto_sluice_builds_blocking_stability_channel(self) -> None:
        sluice = build_veto_sluice(sluice_id="sluice-194-stability")
        channel = next(item for item in sluice.channels if item.sluice_status is SluiceStatus.BLOCKING)

        self.assertIsInstance(sluice, VetoSluice)
        self.assertIsInstance(channel, VetoChannel)
        self.assertEqual(channel.veto_stop, VetoStop.HARD_STOP)
        self.assertEqual(channel.release_path, ReleasePath.EXECUTIVE_RELEASE)
        self.assertEqual(channel.recall_path, RecallPath.IMMEDIATE_RECALL)

    def test_kki_veto_sluice_builds_reviewing_governance_channel(self) -> None:
        sluice = build_veto_sluice(sluice_id="sluice-194-governance")
        channel = next(item for item in sluice.channels if item.sluice_status is SluiceStatus.REVIEWING)

        self.assertEqual(channel.veto_stop, VetoStop.REVIEW_STOP)
        self.assertEqual(channel.release_path, ReleasePath.GOVERNED_RELEASE)
        self.assertEqual(channel.recall_path, RecallPath.GOVERNED_RECALL)
        self.assertGreater(channel.guard_score, 0.6)

    def test_kki_veto_sluice_builds_clearing_autonomy_channel(self) -> None:
        sluice = build_veto_sluice(sluice_id="sluice-194-expansion")
        channel = next(item for item in sluice.channels if item.sluice_status is SluiceStatus.CLEARING)

        self.assertEqual(channel.veto_stop, VetoStop.OPEN_STOP)
        self.assertEqual(channel.release_path, ReleasePath.AUTONOMY_RELEASE)
        self.assertEqual(channel.recall_path, RecallPath.SUPERVISED_RECALL)
        self.assertTrue(channel.release_ready)

    def test_kki_veto_sluice_aggregates_sluice_signal(self) -> None:
        sluice = build_veto_sluice(sluice_id="sluice-194-signal")

        self.assertEqual(sluice.sluice_signal.status, "sluice-blocking")
        self.assertEqual(sluice.blocking_channel_ids, ("sluice-194-signal-stability-lane",))
        self.assertEqual(sluice.reviewing_channel_ids, ("sluice-194-signal-governance-lane",))
        self.assertEqual(sluice.clearing_channel_ids, ("sluice-194-signal-expansion-lane",))

    def test_kki_consensus_diplomacy_builds_deadlocked_stability_channel(self) -> None:
        diplomacy = build_consensus_diplomacy(diplomacy_id="diplomacy-195-stability")
        channel = next(item for item in diplomacy.channels if item.diplomacy_status is DiplomacyStatus.DEADLOCKED)

        self.assertIsInstance(diplomacy, ConsensusDiplomacy)
        self.assertIsInstance(channel, DiplomacyChannel)
        self.assertEqual(channel.posture, DiplomacyPosture.CONTAINMENT_TALKS)
        self.assertEqual(channel.diplomacy_path, DiplomacyPath.VETO_TABLE)

    def test_kki_consensus_diplomacy_builds_brokered_governance_channel(self) -> None:
        diplomacy = build_consensus_diplomacy(diplomacy_id="diplomacy-195-governance")
        channel = next(item for item in diplomacy.channels if item.diplomacy_status is DiplomacyStatus.BROKERED)

        self.assertEqual(channel.posture, DiplomacyPosture.REVIEW_COMPACT)
        self.assertEqual(channel.diplomacy_path, DiplomacyPath.GOVERNANCE_TABLE)
        self.assertGreater(channel.compromise_score, 0.5)

    def test_kki_consensus_diplomacy_builds_harmonized_autonomy_channel(self) -> None:
        diplomacy = build_consensus_diplomacy(diplomacy_id="diplomacy-195-expansion")
        channel = next(item for item in diplomacy.channels if item.diplomacy_status is DiplomacyStatus.HARMONIZED)

        self.assertEqual(channel.posture, DiplomacyPosture.RELEASE_ACCORD)
        self.assertEqual(channel.diplomacy_path, DiplomacyPath.AUTONOMY_TABLE)
        self.assertTrue(channel.release_ready)

    def test_kki_consensus_diplomacy_aggregates_diplomacy_signal(self) -> None:
        diplomacy = build_consensus_diplomacy(diplomacy_id="diplomacy-195-signal")

        self.assertEqual(diplomacy.diplomacy_signal.status, "diplomacy-deadlocked")
        self.assertEqual(diplomacy.deadlocked_channel_ids, ("diplomacy-195-signal-stability-lane",))
        self.assertEqual(diplomacy.brokered_channel_ids, ("diplomacy-195-signal-governance-lane",))
        self.assertEqual(diplomacy.harmonized_channel_ids, ("diplomacy-195-signal-expansion-lane",))

    def test_kki_leitstern_doctrine_builds_guarded_boundary_clause(self) -> None:
        doctrine = build_leitstern_doctrine(doctrine_id="doctrine-196-stability")
        clause = next(item for item in doctrine.clauses if item.doctrine_status is DoctrineStatus.GUARDED)

        self.assertIsInstance(doctrine, LeitsternDoctrine)
        self.assertIsInstance(clause, DoctrineClause)
        self.assertEqual(clause.principle, DoctrinePrinciple.BOUNDARY_PRIMACY)
        self.assertEqual(clause.doctrine_scope, DoctrineScope.STEWARD_CANON)

    def test_kki_leitstern_doctrine_builds_adopted_governance_clause(self) -> None:
        doctrine = build_leitstern_doctrine(doctrine_id="doctrine-196-governance")
        clause = next(item for item in doctrine.clauses if item.doctrine_status is DoctrineStatus.ADOPTED)

        self.assertEqual(clause.principle, DoctrinePrinciple.GOVERNED_ALIGNMENT)
        self.assertEqual(clause.doctrine_scope, DoctrineScope.GOVERNANCE_CANON)
        self.assertGreater(clause.doctrine_strength, 0.5)

    def test_kki_leitstern_doctrine_builds_enshrined_autonomy_clause(self) -> None:
        doctrine = build_leitstern_doctrine(doctrine_id="doctrine-196-expansion")
        clause = next(item for item in doctrine.clauses if item.doctrine_status is DoctrineStatus.ENSHRINED)

        self.assertEqual(clause.principle, DoctrinePrinciple.EXPANSION_DISCIPLINE)
        self.assertEqual(clause.doctrine_scope, DoctrineScope.AUTONOMY_CANON)
        self.assertTrue(clause.release_ready)

    def test_kki_leitstern_doctrine_aggregates_doctrine_signal(self) -> None:
        doctrine = build_leitstern_doctrine(doctrine_id="doctrine-196-signal")

        self.assertEqual(doctrine.doctrine_signal.status, "doctrine-guarded")
        self.assertEqual(doctrine.guarded_clause_ids, ("doctrine-196-signal-stability-lane",))
        self.assertEqual(doctrine.adopted_clause_ids, ("doctrine-196-signal-governance-lane",))
        self.assertEqual(doctrine.enshrined_clause_ids, ("doctrine-196-signal-expansion-lane",))

    def test_kki_missions_collegium_builds_reserved_stability_seat(self) -> None:
        collegium = build_missions_collegium(collegium_id="collegium-197-stability")
        seat = next(item for item in collegium.seats if item.collegium_status is CollegiumStatus.RESERVED)

        self.assertIsInstance(collegium, MissionsCollegium)
        self.assertIsInstance(seat, CollegiumSeat)
        self.assertEqual(seat.collegium_mandate, CollegiumMandate.STABILITY_CHAIR)
        self.assertEqual(seat.collegium_lane, CollegiumLane.CONTAINMENT_PORTFOLIO)
        self.assertEqual(seat.mission_ref, "recovery-drill")

    def test_kki_missions_collegium_builds_coordinating_governance_seat(self) -> None:
        collegium = build_missions_collegium(collegium_id="collegium-197-governance")
        seat = next(item for item in collegium.seats if item.collegium_status is CollegiumStatus.COORDINATING)

        self.assertEqual(seat.collegium_mandate, CollegiumMandate.GOVERNANCE_CHAIR)
        self.assertEqual(seat.collegium_lane, CollegiumLane.GOVERNANCE_PORTFOLIO)
        self.assertEqual(seat.mission_ref, "shadow-hardening")
        self.assertGreater(seat.collegium_weight, 0.3)

    def test_kki_missions_collegium_builds_deployed_autonomy_seat(self) -> None:
        collegium = build_missions_collegium(collegium_id="collegium-197-expansion")
        seat = next(item for item in collegium.seats if item.collegium_status is CollegiumStatus.DEPLOYED)

        self.assertEqual(seat.collegium_mandate, CollegiumMandate.EXPANSION_CHAIR)
        self.assertEqual(seat.collegium_lane, CollegiumLane.EXPANSION_PORTFOLIO)
        self.assertEqual(seat.mission_ref, "pilot-cutover")
        self.assertTrue(seat.release_ready)

    def test_kki_missions_collegium_aggregates_collegium_signal(self) -> None:
        collegium = build_missions_collegium(collegium_id="collegium-197-signal")

        self.assertEqual(collegium.collegium_signal.status, "collegium-reserved")
        self.assertEqual(collegium.reserved_seat_ids, ("collegium-197-signal-stability-lane",))
        self.assertEqual(collegium.coordinating_seat_ids, ("collegium-197-signal-governance-lane",))
        self.assertEqual(collegium.deployed_seat_ids, ("collegium-197-signal-expansion-lane",))

    def test_kki_priority_conclave_builds_guarded_stability_motion(self) -> None:
        conclave = build_priority_conclave(conclave_id="conclave-198-stability")
        motion = next(item for item in conclave.motions if item.conclave_status is ConclaveStatus.GUARDED)

        self.assertIsInstance(conclave, PriorityConclave)
        self.assertIsInstance(motion, ConclaveMotion)
        self.assertEqual(motion.conclave_priority, ConclavePriority.STABILITY_FIRST)
        self.assertEqual(motion.conclave_lane, ConclaveLane.CONTAINMENT_SLOT)
        self.assertEqual(motion.mission_ref, "recovery-drill")

    def test_kki_priority_conclave_builds_shortlisted_governance_motion(self) -> None:
        conclave = build_priority_conclave(conclave_id="conclave-198-governance")
        motion = next(item for item in conclave.motions if item.conclave_status is ConclaveStatus.SHORTLISTED)

        self.assertEqual(motion.conclave_priority, ConclavePriority.GOVERNANCE_FOCUS)
        self.assertEqual(motion.conclave_lane, ConclaveLane.GOVERNANCE_SLOT)
        self.assertEqual(motion.mission_ref, "shadow-hardening")
        self.assertGreater(motion.priority_score, 0.4)

    def test_kki_priority_conclave_builds_elected_autonomy_motion(self) -> None:
        conclave = build_priority_conclave(conclave_id="conclave-198-expansion")
        motion = next(item for item in conclave.motions if item.conclave_status is ConclaveStatus.ELECTED)

        self.assertEqual(motion.conclave_priority, ConclavePriority.RELEASE_VECTOR)
        self.assertEqual(motion.conclave_lane, ConclaveLane.EXPANSION_SLOT)
        self.assertEqual(motion.mission_ref, "pilot-cutover")
        self.assertTrue(motion.release_ready)

    def test_kki_priority_conclave_aggregates_conclave_signal(self) -> None:
        conclave = build_priority_conclave(conclave_id="conclave-198-signal")

        self.assertEqual(conclave.conclave_signal.status, "conclave-guarded")
        self.assertEqual(conclave.guarded_motion_ids, ("conclave-198-signal-stability-lane",))
        self.assertEqual(conclave.shortlisted_motion_ids, ("conclave-198-signal-governance-lane",))
        self.assertEqual(conclave.elected_motion_ids, ("conclave-198-signal-expansion-lane",))

    def test_kki_course_contract_builds_protective_stability_clause(self) -> None:
        contract = build_course_contract(contract_id="contract-199-stability")
        clause = next(item for item in contract.clauses if item.contract_status is ContractStatus.PROTECTIVE)

        self.assertIsInstance(contract, CourseContract)
        self.assertIsInstance(clause, ContractClause)
        self.assertEqual(clause.contract_party, ContractParty.STEWARD_ASSEMBLY)
        self.assertEqual(clause.contract_commitment, ContractCommitment.HOLD_LINE)
        self.assertEqual(clause.mission_ref, "recovery-drill")

    def test_kki_course_contract_builds_operative_governance_clause(self) -> None:
        contract = build_course_contract(contract_id="contract-199-governance")
        clause = next(item for item in contract.clauses if item.contract_status is ContractStatus.OPERATIVE)

        self.assertEqual(clause.contract_party, ContractParty.GOVERNANCE_ASSEMBLY)
        self.assertEqual(clause.contract_commitment, ContractCommitment.ALIGN_LINE)
        self.assertEqual(clause.mission_ref, "shadow-hardening")
        self.assertGreater(clause.contract_strength, 0.4)

    def test_kki_course_contract_builds_binding_autonomy_clause(self) -> None:
        contract = build_course_contract(contract_id="contract-199-expansion")
        clause = next(item for item in contract.clauses if item.contract_status is ContractStatus.BINDING)

        self.assertEqual(clause.contract_party, ContractParty.AUTONOMY_ASSEMBLY)
        self.assertEqual(clause.contract_commitment, ContractCommitment.ADVANCE_LINE)
        self.assertEqual(clause.mission_ref, "pilot-cutover")
        self.assertTrue(clause.release_ready)

    def test_kki_course_contract_aggregates_contract_signal(self) -> None:
        contract = build_course_contract(contract_id="contract-199-signal")

        self.assertEqual(contract.contract_signal.status, "contract-protective")
        self.assertEqual(contract.protective_clause_ids, ("contract-199-signal-stability-lane",))
        self.assertEqual(contract.operative_clause_ids, ("contract-199-signal-governance-lane",))
        self.assertEqual(contract.binding_clause_ids, ("contract-199-signal-expansion-lane",))

    def test_kki_leitstern_codex_builds_guarded_decision_section(self) -> None:
        codex = build_leitstern_codex(codex_id="codex-200-stability")
        section = next(item for item in codex.sections if item.codex_status is CodexStatus.GUARDED)

        self.assertIsInstance(codex, LeitsternCodex)
        self.assertIsInstance(section, CodexSection)
        self.assertEqual(section.codex_canon, CodexCanon.DECISION_CANON)
        self.assertEqual(section.codex_axis, CodexAxis.DECISION_ORDER)
        self.assertEqual(section.mission_ref, "recovery-drill")

    def test_kki_leitstern_codex_builds_governed_delegation_section(self) -> None:
        codex = build_leitstern_codex(codex_id="codex-200-governance")
        section = next(item for item in codex.sections if item.codex_status is CodexStatus.GOVERNED)

        self.assertEqual(section.codex_canon, CodexCanon.GOVERNANCE_CANON)
        self.assertEqual(section.codex_axis, CodexAxis.DELEGATION_ORDER)
        self.assertEqual(section.mission_ref, "shadow-hardening")
        self.assertGreater(section.codex_strength, 0.4)

    def test_kki_leitstern_codex_builds_canonical_diplomacy_section(self) -> None:
        codex = build_leitstern_codex(codex_id="codex-200-expansion")
        section = next(item for item in codex.sections if item.codex_status is CodexStatus.CANONICAL)

        self.assertEqual(section.codex_canon, CodexCanon.EXPANSION_CANON)
        self.assertEqual(section.codex_axis, CodexAxis.DIPLOMACY_ORDER)
        self.assertEqual(section.mission_ref, "pilot-cutover")
        self.assertTrue(section.release_ready)

    def test_kki_leitstern_codex_aggregates_codex_signal(self) -> None:
        codex = build_leitstern_codex(codex_id="codex-200-signal")

        self.assertEqual(codex.codex_signal.status, "codex-guarded")
        self.assertEqual(codex.guarded_section_ids, ("codex-200-signal-stability-lane",))
        self.assertEqual(codex.governed_section_ids, ("codex-200-signal-governance-lane",))
        self.assertEqual(codex.canonical_section_ids, ("codex-200-signal-expansion-lane",))

    def test_kki_kodex_register_builds_reserved_decision_entry(self) -> None:
        register = build_kodex_register(register_id="register-201-stability")
        entry = next(item for item in register.entries if item.register_tier is RegisterTier.RESERVED)

        self.assertIsInstance(register, KodexRegister)
        self.assertIsInstance(entry, KodexRegisterEntry)
        self.assertEqual(entry.codex_canon, CodexCanon.DECISION_CANON)
        self.assertEqual(entry.retention, RegisterRetention.AUDIT)
        self.assertEqual(entry.version, "v1.1")

    def test_kki_kodex_register_builds_curated_governance_entry(self) -> None:
        register = build_kodex_register(register_id="register-201-governance")
        entry = next(item for item in register.entries if item.register_tier is RegisterTier.CURATED)

        self.assertEqual(entry.codex_canon, CodexCanon.GOVERNANCE_CANON)
        self.assertEqual(entry.retention, RegisterRetention.GOVERNANCE)
        self.assertGreater(entry.register_weight, 0.4)

    def test_kki_kodex_register_builds_canonized_expansion_entry(self) -> None:
        register = build_kodex_register(register_id="register-201-expansion")
        entry = next(item for item in register.entries if item.register_tier is RegisterTier.CANONIZED)

        self.assertEqual(entry.codex_canon, CodexCanon.EXPANSION_CANON)
        self.assertEqual(entry.retention, RegisterRetention.CONSTITUTIONAL)
        self.assertTrue(entry.release_ready)

    def test_kki_kodex_register_aggregates_register_signal(self) -> None:
        register = build_kodex_register(register_id="register-201-signal")

        self.assertEqual(register.register_signal.status, "register-reserved")
        self.assertEqual(register.reserved_entry_ids, ("register-201-signal-stability-lane",))
        self.assertEqual(register.curated_entry_ids, ("register-201-signal-governance-lane",))
        self.assertEqual(register.canonized_entry_ids, ("register-201-signal-expansion-lane",))

    def test_kki_satzungs_rat_builds_provisional_steward_article(self) -> None:
        rat = build_satzungs_rat(rat_id="rat-202-stability")
        article = next(item for item in rat.articles if item.rat_status is RatStatus.PROVISIONAL)

        self.assertIsInstance(rat, SatzungsRat)
        self.assertIsInstance(article, SatzungsRatArticle)
        self.assertEqual(article.bench, RatBench.STEWARD_BENCH)
        self.assertEqual(article.interpretation, RatInterpretation.PROTECTIVE_READING)
        self.assertEqual(article.precedent_window, 1)

    def test_kki_satzungs_rat_builds_ratified_governance_article(self) -> None:
        rat = build_satzungs_rat(rat_id="rat-202-governance")
        article = next(item for item in rat.articles if item.rat_status is RatStatus.RATIFIED)

        self.assertEqual(article.bench, RatBench.GOVERNANCE_BENCH)
        self.assertEqual(article.interpretation, RatInterpretation.GOVERNED_READING)
        self.assertGreater(article.statute_weight, 0.45)

    def test_kki_satzungs_rat_builds_enshrined_autonomy_article(self) -> None:
        rat = build_satzungs_rat(rat_id="rat-202-expansion")
        article = next(item for item in rat.articles if item.rat_status is RatStatus.ENSHRINED)

        self.assertEqual(article.bench, RatBench.AUTONOMY_BENCH)
        self.assertEqual(article.interpretation, RatInterpretation.SOVEREIGN_READING)
        self.assertTrue(article.release_ready)

    def test_kki_satzungs_rat_aggregates_rat_signal(self) -> None:
        rat = build_satzungs_rat(rat_id="rat-202-signal")

        self.assertEqual(rat.rat_signal.status, "rat-provisional")
        self.assertEqual(rat.provisional_article_ids, ("rat-202-signal-stability-lane",))
        self.assertEqual(rat.ratified_article_ids, ("rat-202-signal-governance-lane",))
        self.assertEqual(rat.enshrined_article_ids, ("rat-202-signal-expansion-lane",))

    def test_kki_mandats_konvent_builds_begrenzt_steward_line(self) -> None:
        konvent = build_mandats_konvent(konvent_id="konvent-203-stability")
        line = next(item for item in konvent.lines if item.konvent_status is KonventStatus.BEGRENZT)

        self.assertIsInstance(konvent, MandatsKonvent)
        self.assertIsInstance(line, MandatsLinie)
        self.assertEqual(line.konvent_mandat, KonventMandat.SCHUTZ_MANDAT)
        self.assertEqual(line.konvent_ebene, KonventEbene.STEWARD_EBENE)
        self.assertEqual(line.handoff_window, 1)

    def test_kki_mandats_konvent_builds_delegiert_governance_line(self) -> None:
        konvent = build_mandats_konvent(konvent_id="konvent-203-governance")
        line = next(item for item in konvent.lines if item.konvent_status is KonventStatus.DELEGIERT)

        self.assertEqual(line.konvent_mandat, KonventMandat.ORDNUNGS_MANDAT)
        self.assertEqual(line.konvent_ebene, KonventEbene.GOVERNANCE_EBENE)
        self.assertGreater(line.delegations_budget, 0.5)

    def test_kki_mandats_konvent_builds_verankert_autonomy_line(self) -> None:
        konvent = build_mandats_konvent(konvent_id="konvent-203-expansion")
        line = next(item for item in konvent.lines if item.konvent_status is KonventStatus.VERANKERT)

        self.assertEqual(line.konvent_mandat, KonventMandat.SOUVERAENITAETS_MANDAT)
        self.assertEqual(line.konvent_ebene, KonventEbene.AUTONOMIE_EBENE)
        self.assertTrue(line.release_ready)

    def test_kki_mandats_konvent_aggregates_konvent_signal(self) -> None:
        konvent = build_mandats_konvent(konvent_id="konvent-203-signal")

        self.assertEqual(konvent.konvent_signal.status, "konvent-begrenzt")
        self.assertEqual(konvent.begrenzt_line_ids, ("konvent-203-signal-stability-lane",))
        self.assertEqual(konvent.delegiert_line_ids, ("konvent-203-signal-governance-lane",))
        self.assertEqual(konvent.verankert_line_ids, ("konvent-203-signal-expansion-lane",))

    def test_kki_ereignishorizont_norm_builds_gesperrt_schutz_norm(self) -> None:
        norm = build_ereignishorizont_norm(norm_id="horizont-278-stability")
        eintrag = next(n for n in norm.normen if n.geltung is EreignishorizontGeltung.GESPERRT)

        self.assertIsInstance(norm, EreignishorizontNorm)
        self.assertIsInstance(eintrag, EreignishorizontNormEintrag)
        self.assertEqual(eintrag.ereignishorizont_typ, EreignishorizontTyp.SCHUTZ_HORIZONT)
        self.assertEqual(eintrag.prozedur, EreignishorizontProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.ereignishorizont_tier, 1)

    def test_kki_ereignishorizont_norm_builds_horizontiert_ordnungs_norm(self) -> None:
        norm = build_ereignishorizont_norm(norm_id="horizont-278-governance")
        eintrag = next(n for n in norm.normen if n.geltung is EreignishorizontGeltung.HORIZONTIERT)

        self.assertEqual(eintrag.ereignishorizont_typ, EreignishorizontTyp.ORDNUNGS_HORIZONT)
        self.assertEqual(eintrag.prozedur, EreignishorizontProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.ereignishorizont_weight, 0.0)

    def test_kki_ereignishorizont_norm_builds_grundlegend_souveraenitaets_norm(self) -> None:
        norm = build_ereignishorizont_norm(norm_id="horizont-278-expansion")
        eintrag = next(n for n in norm.normen if n.geltung is EreignishorizontGeltung.GRUNDLEGEND_HORIZONTIERT)

        self.assertEqual(eintrag.ereignishorizont_typ, EreignishorizontTyp.SOUVERAENITAETS_HORIZONT)
        self.assertEqual(eintrag.prozedur, EreignishorizontProzedur.PLENARPROTOKOLL)
        self.assertTrue(eintrag.canonical)

    def test_kki_ereignishorizont_norm_aggregates_norm_signal(self) -> None:
        norm = build_ereignishorizont_norm(norm_id="horizont-278-signal")

        self.assertEqual(norm.norm_signal.status, "norm-gesperrt")
        self.assertEqual(norm.gesperrt_norm_ids, ("horizont-278-signal-stability-lane",))
        self.assertEqual(norm.horizontiert_norm_ids, ("horizont-278-signal-governance-lane",))
        self.assertEqual(norm.grundlegend_norm_ids, ("horizont-278-signal-expansion-lane",))

    def test_kki_schwarzes_loch_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_schwarzes_loch_senat(senat_id="senat-277-stability")
        norm = next(n for n in senat.normen if n.geltung is SchwarzsLochGeltung.GESPERRT)

        self.assertIsInstance(senat, SchwarzeLoechSenat)
        self.assertIsInstance(norm, SchwarzsLochNorm)
        self.assertEqual(norm.schwarzes_loch_typ, SchwarzsLochTyp.SCHUTZ_SCHWARZES_LOCH)
        self.assertEqual(norm.prozedur, SchwarzsLochProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.schwarzes_loch_tier, 1)

    def test_kki_schwarzes_loch_senat_builds_absorbiert_ordnungs_norm(self) -> None:
        senat = build_schwarzes_loch_senat(senat_id="senat-277-governance")
        norm = next(n for n in senat.normen if n.geltung is SchwarzsLochGeltung.ABSORBIERT)

        self.assertEqual(norm.schwarzes_loch_typ, SchwarzsLochTyp.ORDNUNGS_SCHWARZES_LOCH)
        self.assertEqual(norm.prozedur, SchwarzsLochProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.schwarzes_loch_weight, 0.0)

    def test_kki_schwarzes_loch_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_schwarzes_loch_senat(senat_id="senat-277-expansion")
        norm = next(n for n in senat.normen if n.geltung is SchwarzsLochGeltung.GRUNDLEGEND_ABSORBIERT)

        self.assertEqual(norm.schwarzes_loch_typ, SchwarzsLochTyp.SOUVERAENITAETS_SCHWARZES_LOCH)
        self.assertEqual(norm.prozedur, SchwarzsLochProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_schwarzes_loch_senat_aggregates_senat_signal(self) -> None:
        senat = build_schwarzes_loch_senat(senat_id="senat-277-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-277-signal-stability-lane",))
        self.assertEqual(senat.absorbiert_norm_ids, ("senat-277-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-277-signal-expansion-lane",))

    def test_kki_singularitaets_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_singularitaets_manifest(manifest_id="manifest-276-stability")
        norm = next(n for n in manifest.normen if n.geltung is SingularitaetsGeltung.GESPERRT)

        self.assertIsInstance(manifest, SingularitaetsManifest)
        self.assertIsInstance(norm, SingularitaetsNorm)
        self.assertEqual(norm.singularitaets_typ, SingularitaetsTyp.SCHUTZ_SINGULARITAET)
        self.assertEqual(norm.prozedur, SingularitaetsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.singularitaets_tier, 1)

    def test_kki_singularitaets_manifest_builds_singulaer_ordnungs_norm(self) -> None:
        manifest = build_singularitaets_manifest(manifest_id="manifest-276-governance")
        norm = next(n for n in manifest.normen if n.geltung is SingularitaetsGeltung.SINGULAER)

        self.assertEqual(norm.singularitaets_typ, SingularitaetsTyp.ORDNUNGS_SINGULARITAET)
        self.assertEqual(norm.prozedur, SingularitaetsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.singularitaets_weight, 0.0)

    def test_kki_singularitaets_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_singularitaets_manifest(manifest_id="manifest-276-expansion")
        norm = next(n for n in manifest.normen if n.geltung is SingularitaetsGeltung.GRUNDLEGEND_SINGULAER)

        self.assertEqual(norm.singularitaets_typ, SingularitaetsTyp.SOUVERAENITAETS_SINGULARITAET)
        self.assertEqual(norm.prozedur, SingularitaetsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_singularitaets_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_singularitaets_manifest(manifest_id="manifest-276-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-276-signal-stability-lane",))
        self.assertEqual(manifest.singulaer_norm_ids, ("manifest-276-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-276-signal-expansion-lane",))

    def test_kki_thermodynamik_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_thermodynamik_verfassung(verfassung_id="verfassung-290-stability")
        norm = next(n for n in verfassung.normen if n.geltung is ThermoverfassungsGeltung.GESPERRT)

        self.assertIsInstance(verfassung, ThermodynamikVerfassung)
        self.assertIsInstance(norm, ThermoverfassungsNorm)
        self.assertEqual(norm.thermoverfassungs_typ, ThermoverfassungsTyp.SCHUTZ_THERMOVERFASSUNG)
        self.assertEqual(norm.prozedur, ThermoverfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.thermoverfassungs_tier, 1)

    def test_kki_thermodynamik_verfassung_builds_thermoverfasst_ordnungs_norm(self) -> None:
        verfassung = build_thermodynamik_verfassung(verfassung_id="verfassung-290-governance")
        norm = next(n for n in verfassung.normen if n.geltung is ThermoverfassungsGeltung.THERMOVERFASST)

        self.assertEqual(norm.thermoverfassungs_typ, ThermoverfassungsTyp.ORDNUNGS_THERMOVERFASSUNG)
        self.assertEqual(norm.prozedur, ThermoverfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.thermoverfassungs_weight, 0.0)

    def test_kki_thermodynamik_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_thermodynamik_verfassung(verfassung_id="verfassung-290-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is ThermoverfassungsGeltung.GRUNDLEGEND_THERMOVERFASST)

        self.assertEqual(norm.thermoverfassungs_typ, ThermoverfassungsTyp.SOUVERAENITAETS_THERMOVERFASSUNG)
        self.assertEqual(norm.prozedur, ThermoverfassungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_thermodynamik_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_thermodynamik_verfassung(verfassung_id="verfassung-290-signal")

        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-290-signal-stability-lane",))
        self.assertEqual(verfassung.thermoverfasst_norm_ids, ("verfassung-290-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-290-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #291 ElektromagnetikFeld
    # ------------------------------------------------------------------

    def test_kki_elektromagnetik_feld_builds_gesperrt_schutz_norm(self) -> None:
        feld = build_elektromagnetik_feld(feld_id="feld-291-stability")
        norm = next(n for n in feld.normen if n.geltung is ElektromagnetikGeltung.GESPERRT)

        self.assertIsInstance(feld, ElektromagnetikFeld)
        self.assertIsInstance(norm, ElektromagnetikNorm)
        self.assertEqual(norm.elektromagnetik_typ, ElektromagnetikTyp.SCHUTZ_ELEKTROMAGNETIK)
        self.assertEqual(norm.prozedur, ElektromagnetikProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.elektromagnetik_tier, 1)

    def test_kki_elektromagnetik_feld_builds_elektromagnetisch_ordnungs_norm(self) -> None:
        feld = build_elektromagnetik_feld(feld_id="feld-291-governance")
        norm = next(n for n in feld.normen if n.geltung is ElektromagnetikGeltung.ELEKTROMAGNETISCH)

        self.assertEqual(norm.elektromagnetik_typ, ElektromagnetikTyp.ORDNUNGS_ELEKTROMAGNETIK)
        self.assertEqual(norm.prozedur, ElektromagnetikProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.elektromagnetik_weight, 0.0)

    def test_kki_elektromagnetik_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        feld = build_elektromagnetik_feld(feld_id="feld-291-expansion")
        norm = next(n for n in feld.normen if n.geltung is ElektromagnetikGeltung.GRUNDLEGEND_ELEKTROMAGNETISCH)

        self.assertEqual(norm.elektromagnetik_typ, ElektromagnetikTyp.SOUVERAENITAETS_ELEKTROMAGNETIK)
        self.assertEqual(norm.prozedur, ElektromagnetikProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_elektromagnetik_feld_aggregates_feld_signal(self) -> None:
        feld = build_elektromagnetik_feld(feld_id="feld-291-signal")

        self.assertEqual(feld.feld_signal.status, "feld-gesperrt")
        self.assertEqual(feld.gesperrt_norm_ids, ("feld-291-signal-stability-lane",))
        self.assertEqual(feld.elektromagnetisch_norm_ids, ("feld-291-signal-governance-lane",))
        self.assertEqual(feld.grundlegend_norm_ids, ("feld-291-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #292 LadungsRegister
    # ------------------------------------------------------------------

    def test_kki_ladungs_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_ladungs_register(register_id="register-292-stability")
        norm = next(n for n in register.normen if n.geltung is LadungsGeltung.GESPERRT)

        self.assertIsInstance(register, LadungsRegister)
        self.assertIsInstance(norm, LadungsNorm)
        self.assertEqual(norm.ladungs_typ, LadungsTyp.SCHUTZ_LADUNG)
        self.assertEqual(norm.prozedur, LadungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.ladungs_tier, 1)

    def test_kki_ladungs_register_builds_geladen_ordnungs_norm(self) -> None:
        register = build_ladungs_register(register_id="register-292-governance")
        norm = next(n for n in register.normen if n.geltung is LadungsGeltung.GELADEN)

        self.assertEqual(norm.ladungs_typ, LadungsTyp.ORDNUNGS_LADUNG)
        self.assertEqual(norm.prozedur, LadungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.ladungs_weight, 0.0)

    def test_kki_ladungs_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_ladungs_register(register_id="register-292-expansion")
        norm = next(n for n in register.normen if n.geltung is LadungsGeltung.GRUNDLEGEND_GELADEN)

        self.assertEqual(norm.ladungs_typ, LadungsTyp.SOUVERAENITAETS_LADUNG)
        self.assertEqual(norm.prozedur, LadungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_ladungs_register_aggregates_register_signal(self) -> None:
        register = build_ladungs_register(register_id="register-292-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-292-signal-stability-lane",))
        self.assertEqual(register.geladen_norm_ids, ("register-292-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-292-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #293 MaxwellCharta
    # ------------------------------------------------------------------

    def test_kki_maxwell_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_maxwell_charta(charta_id="charta-293-stability")
        norm = next(n for n in charta.normen if n.geltung is MaxwellGeltung.GESPERRT)

        self.assertIsInstance(charta, MaxwellCharta)
        self.assertIsInstance(norm, MaxwellNorm)
        self.assertEqual(norm.maxwell_typ, MaxwellTyp.SCHUTZ_MAXWELL)
        self.assertEqual(norm.prozedur, MaxwellProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.maxwell_tier, 1)

    def test_kki_maxwell_charta_builds_maxwellisch_ordnungs_norm(self) -> None:
        charta = build_maxwell_charta(charta_id="charta-293-governance")
        norm = next(n for n in charta.normen if n.geltung is MaxwellGeltung.MAXWELLISCH)

        self.assertEqual(norm.maxwell_typ, MaxwellTyp.ORDNUNGS_MAXWELL)
        self.assertEqual(norm.prozedur, MaxwellProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.maxwell_weight, 0.0)

    def test_kki_maxwell_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_maxwell_charta(charta_id="charta-293-expansion")
        norm = next(n for n in charta.normen if n.geltung is MaxwellGeltung.GRUNDLEGEND_MAXWELLISCH)

        self.assertEqual(norm.maxwell_typ, MaxwellTyp.SOUVERAENITAETS_MAXWELL)
        self.assertEqual(norm.prozedur, MaxwellProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_maxwell_charta_aggregates_charta_signal(self) -> None:
        charta = build_maxwell_charta(charta_id="charta-293-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-293-signal-stability-lane",))
        self.assertEqual(charta.maxwellisch_norm_ids, ("charta-293-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-293-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #294 InduktionsKodex
    # ------------------------------------------------------------------

    def test_kki_induktions_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_induktions_kodex(kodex_id="kodex-294-stability")
        norm = next(n for n in kodex.normen if n.geltung is InduktionsGeltung.GESPERRT)

        self.assertIsInstance(kodex, InduktionsKodex)
        self.assertIsInstance(norm, InduktionsNorm)
        self.assertEqual(norm.induktions_typ, InduktionsTyp.SCHUTZ_INDUKTION)
        self.assertEqual(norm.prozedur, InduktionsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.induktions_tier, 1)

    def test_kki_induktions_kodex_builds_induziert_ordnungs_norm(self) -> None:
        kodex = build_induktions_kodex(kodex_id="kodex-294-governance")
        norm = next(n for n in kodex.normen if n.geltung is InduktionsGeltung.INDUZIERT)

        self.assertEqual(norm.induktions_typ, InduktionsTyp.ORDNUNGS_INDUKTION)
        self.assertEqual(norm.prozedur, InduktionsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.induktions_weight, 0.0)

    def test_kki_induktions_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_induktions_kodex(kodex_id="kodex-294-expansion")
        norm = next(n for n in kodex.normen if n.geltung is InduktionsGeltung.GRUNDLEGEND_INDUZIERT)

        self.assertEqual(norm.induktions_typ, InduktionsTyp.SOUVERAENITAETS_INDUKTION)
        self.assertEqual(norm.prozedur, InduktionsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_induktions_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_induktions_kodex(kodex_id="kodex-294-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-294-signal-stability-lane",))
        self.assertEqual(kodex.induziert_norm_ids, ("kodex-294-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-294-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #295 WellenausbreitungsPakt
    # ------------------------------------------------------------------

    def test_kki_wellenausbreitung_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_wellenausbreitung_pakt(pakt_id="pakt-295-stability")
        norm = next(n for n in pakt.normen if n.geltung is WellenausbreitungsGeltung.GESPERRT)

        self.assertIsInstance(pakt, WellenausbreitungsPakt)
        self.assertIsInstance(norm, WellenausbreitungsNorm)
        self.assertEqual(norm.wellenausbreitung_typ, WellenausbreitungsTyp.SCHUTZ_WELLENAUSBREITUNG)
        self.assertEqual(norm.prozedur, WellenausbreitungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.wellenausbreitung_tier, 1)

    def test_kki_wellenausbreitung_pakt_builds_wellenausbreitend_ordnungs_norm(self) -> None:
        pakt = build_wellenausbreitung_pakt(pakt_id="pakt-295-governance")
        norm = next(n for n in pakt.normen if n.geltung is WellenausbreitungsGeltung.WELLENAUSBREITEND)

        self.assertEqual(norm.wellenausbreitung_typ, WellenausbreitungsTyp.ORDNUNGS_WELLENAUSBREITUNG)
        self.assertEqual(norm.prozedur, WellenausbreitungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.wellenausbreitung_weight, 0.0)

    def test_kki_wellenausbreitung_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_wellenausbreitung_pakt(pakt_id="pakt-295-expansion")
        norm = next(n for n in pakt.normen if n.geltung is WellenausbreitungsGeltung.GRUNDLEGEND_WELLENAUSBREITEND)

        self.assertEqual(norm.wellenausbreitung_typ, WellenausbreitungsTyp.SOUVERAENITAETS_WELLENAUSBREITUNG)
        self.assertEqual(norm.prozedur, WellenausbreitungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_wellenausbreitung_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_wellenausbreitung_pakt(pakt_id="pakt-295-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-295-signal-stability-lane",))
        self.assertEqual(pakt.wellenausbreitend_norm_ids, ("pakt-295-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-295-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #296 LichtgeschwindigkeitsManifest
    # ------------------------------------------------------------------

    def test_kki_lichtgeschwindigkeits_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_lichtgeschwindigkeits_manifest(manifest_id="manifest-296-stability")
        norm = next(n for n in manifest.normen if n.geltung is LichtgeschwindigkeitsGeltung.GESPERRT)

        self.assertIsInstance(manifest, LichtgeschwindigkeitsManifest)
        self.assertIsInstance(norm, LichtgeschwindigkeitsNorm)
        self.assertEqual(norm.lichtgeschwindigkeits_typ, LichtgeschwindigkeitsTyp.SCHUTZ_LICHTGESCHWINDIGKEIT)
        self.assertEqual(norm.prozedur, LichtgeschwindigkeitsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.lichtgeschwindigkeits_tier, 1)

    def test_kki_lichtgeschwindigkeits_manifest_builds_lichtschnell_ordnungs_norm(self) -> None:
        manifest = build_lichtgeschwindigkeits_manifest(manifest_id="manifest-296-governance")
        norm = next(n for n in manifest.normen if n.geltung is LichtgeschwindigkeitsGeltung.LICHTSCHNELL)

        self.assertEqual(norm.lichtgeschwindigkeits_typ, LichtgeschwindigkeitsTyp.ORDNUNGS_LICHTGESCHWINDIGKEIT)
        self.assertEqual(norm.prozedur, LichtgeschwindigkeitsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.lichtgeschwindigkeits_weight, 0.0)

    def test_kki_lichtgeschwindigkeits_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_lichtgeschwindigkeits_manifest(manifest_id="manifest-296-expansion")
        norm = next(n for n in manifest.normen if n.geltung is LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL)

        self.assertEqual(norm.lichtgeschwindigkeits_typ, LichtgeschwindigkeitsTyp.SOUVERAENITAETS_LICHTGESCHWINDIGKEIT)
        self.assertEqual(norm.prozedur, LichtgeschwindigkeitsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_lichtgeschwindigkeits_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_lichtgeschwindigkeits_manifest(manifest_id="manifest-296-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-296-signal-stability-lane",))
        self.assertEqual(manifest.lichtschnell_norm_ids, ("manifest-296-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-296-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #297 SpektralSenat
    # ------------------------------------------------------------------

    def test_kki_spektral_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_spektral_senat(senat_id="senat-297-stability")
        norm = next(n for n in senat.normen if n.geltung is SpektralGeltung.GESPERRT)

        self.assertIsInstance(senat, SpektralSenat)
        self.assertIsInstance(norm, SpektralNorm)
        self.assertEqual(norm.spektral_typ, SpektralTyp.SCHUTZ_SPEKTRUM)
        self.assertEqual(norm.prozedur, SpektralProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.spektral_tier, 1)

    def test_kki_spektral_senat_builds_spektral_ordnungs_norm(self) -> None:
        senat = build_spektral_senat(senat_id="senat-297-governance")
        norm = next(n for n in senat.normen if n.geltung is SpektralGeltung.SPEKTRAL)

        self.assertEqual(norm.spektral_typ, SpektralTyp.ORDNUNGS_SPEKTRUM)
        self.assertEqual(norm.prozedur, SpektralProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.spektral_weight, 0.0)

    def test_kki_spektral_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_spektral_senat(senat_id="senat-297-expansion")
        norm = next(n for n in senat.normen if n.geltung is SpektralGeltung.GRUNDLEGEND_SPEKTRAL)

        self.assertEqual(norm.spektral_typ, SpektralTyp.SOUVERAENITAETS_SPEKTRUM)
        self.assertEqual(norm.prozedur, SpektralProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_spektral_senat_aggregates_senat_signal(self) -> None:
        senat = build_spektral_senat(senat_id="senat-297-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-297-signal-stability-lane",))
        self.assertEqual(senat.spektral_norm_ids, ("senat-297-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-297-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #298 PhotonNorm (*_norm-Muster)
    # ------------------------------------------------------------------

    def test_kki_photon_norm_builds_gesperrt_schutz_eintrag(self) -> None:
        satz = build_photon_norm(norm_id="photon-norm-298-stability")
        eintrag = next(n for n in satz.normen if n.geltung is PhotonNormGeltung.GESPERRT)

        self.assertIsInstance(satz, PhotonNormSatz)
        self.assertIsInstance(eintrag, PhotonNormEintrag)
        self.assertEqual(eintrag.photon_norm_typ, PhotonNormTyp.SCHUTZ_PHOTONNORM)
        self.assertEqual(eintrag.prozedur, PhotonNormProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.photon_norm_tier, 1)

    def test_kki_photon_norm_builds_photonisch_ordnungs_eintrag(self) -> None:
        satz = build_photon_norm(norm_id="photon-norm-298-governance")
        eintrag = next(n for n in satz.normen if n.geltung is PhotonNormGeltung.PHOTONISCH)

        self.assertEqual(eintrag.photon_norm_typ, PhotonNormTyp.ORDNUNGS_PHOTONNORM)
        self.assertEqual(eintrag.prozedur, PhotonNormProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.photon_norm_weight, 0.0)

    def test_kki_photon_norm_builds_grundlegend_souveraenitaets_eintrag(self) -> None:
        satz = build_photon_norm(norm_id="photon-norm-298-expansion")
        eintrag = next(n for n in satz.normen if n.geltung is PhotonNormGeltung.GRUNDLEGEND_PHOTONISCH)

        self.assertEqual(eintrag.photon_norm_typ, PhotonNormTyp.SOUVERAENITAETS_PHOTONNORM)
        self.assertEqual(eintrag.prozedur, PhotonNormProzedur.PLENARPROTOKOLL)
        self.assertTrue(eintrag.canonical)

    def test_kki_photon_norm_aggregates_norm_signal(self) -> None:
        satz = build_photon_norm(norm_id="photon-norm-298-signal")

        self.assertEqual(satz.norm_signal.status, "norm-gesperrt")
        self.assertEqual(satz.gesperrt_norm_ids, ("photon-norm-298-signal-stability-lane",))
        self.assertEqual(satz.photonisch_norm_ids, ("photon-norm-298-signal-governance-lane",))
        self.assertEqual(satz.grundlegend_norm_ids, ("photon-norm-298-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #299 PhotoeffektCharta
    # ------------------------------------------------------------------

    def test_kki_photoeffekt_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_photoeffekt_charta(charta_id="charta-299-stability")
        norm = next(n for n in charta.normen if n.geltung is PhotoeffektGeltung.GESPERRT)

        self.assertIsInstance(charta, PhotoeffektCharta)
        self.assertIsInstance(norm, PhotoeffektNorm)
        self.assertEqual(norm.photoeffekt_typ, PhotoeffektTyp.SCHUTZ_PHOTOEFFEKT)
        self.assertEqual(norm.prozedur, PhotoeffektProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.photoeffekt_tier, 1)

    def test_kki_photoeffekt_charta_builds_photoeffektiv_ordnungs_norm(self) -> None:
        charta = build_photoeffekt_charta(charta_id="charta-299-governance")
        norm = next(n for n in charta.normen if n.geltung is PhotoeffektGeltung.PHOTOEFFEKTIV)

        self.assertEqual(norm.photoeffekt_typ, PhotoeffektTyp.ORDNUNGS_PHOTOEFFEKT)
        self.assertEqual(norm.prozedur, PhotoeffektProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.photoeffekt_weight, 0.0)

    def test_kki_photoeffekt_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_photoeffekt_charta(charta_id="charta-299-expansion")
        norm = next(n for n in charta.normen if n.geltung is PhotoeffektGeltung.GRUNDLEGEND_PHOTOEFFEKTIV)

        self.assertEqual(norm.photoeffekt_typ, PhotoeffektTyp.SOUVERAENITAETS_PHOTOEFFEKT)
        self.assertEqual(norm.prozedur, PhotoeffektProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_photoeffekt_charta_aggregates_charta_signal(self) -> None:
        charta = build_photoeffekt_charta(charta_id="charta-299-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-299-signal-stability-lane",))
        self.assertEqual(charta.photoeffektiv_norm_ids, ("charta-299-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-299-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #300 ElektromagnetikVerfassung – Block-Krone
    # ------------------------------------------------------------------

    def test_kki_elektromagnetik_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_elektromagnetik_verfassung(verfassung_id="verfassung-300-stability")
        norm = next(n for n in verfassung.normen if n.geltung is ElektroverfassungsGeltung.GESPERRT)

        self.assertIsInstance(verfassung, ElektromagnetikVerfassung)
        self.assertIsInstance(norm, ElektroverfassungsNorm)
        self.assertEqual(norm.elektroverfassungs_typ, ElektroverfassungsTyp.SCHUTZ_ELEKTROVERFASSUNG)
        self.assertEqual(norm.prozedur, ElektroverfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.elektroverfassungs_tier, 1)

    def test_kki_elektromagnetik_verfassung_builds_elektroverfasst_ordnungs_norm(self) -> None:
        verfassung = build_elektromagnetik_verfassung(verfassung_id="verfassung-300-governance")
        norm = next(n for n in verfassung.normen if n.geltung is ElektroverfassungsGeltung.ELEKTROVERFASST)

        self.assertEqual(norm.elektroverfassungs_typ, ElektroverfassungsTyp.ORDNUNGS_ELEKTROVERFASSUNG)
        self.assertEqual(norm.prozedur, ElektroverfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.elektroverfassungs_weight, 0.0)

    def test_kki_elektromagnetik_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_elektromagnetik_verfassung(verfassung_id="verfassung-300-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is ElektroverfassungsGeltung.GRUNDLEGEND_ELEKTROVERFASST)

        self.assertEqual(norm.elektroverfassungs_typ, ElektroverfassungsTyp.SOUVERAENITAETS_ELEKTROVERFASSUNG)
        self.assertEqual(norm.prozedur, ElektroverfassungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_elektromagnetik_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_elektromagnetik_verfassung(verfassung_id="verfassung-300-signal")

        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-300-signal-stability-lane",))
        self.assertEqual(verfassung.elektroverfasst_norm_ids, ("verfassung-300-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-300-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #301 KernphysikFeld
    # ------------------------------------------------------------------

    def test_kki_kernphysik_feld_builds_gesperrt_schutz_norm(self) -> None:
        feld = build_kernphysik_feld(feld_id="feld-301-stability")
        norm = next(n for n in feld.normen if n.geltung is KernphysikGeltung.GESPERRT)

        self.assertIsInstance(feld, KernphysikFeld)
        self.assertIsInstance(norm, KernphysikNorm)
        self.assertEqual(norm.kernphysik_typ, KernphysikTyp.SCHUTZ_KERNPHYSIK)
        self.assertEqual(norm.prozedur, KernphysikProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kernphysik_tier, 1)

    def test_kki_kernphysik_feld_builds_kernphysikalisch_ordnungs_norm(self) -> None:
        feld = build_kernphysik_feld(feld_id="feld-301-governance")
        norm = next(n for n in feld.normen if n.geltung is KernphysikGeltung.KERNPHYSIKALISCH)

        self.assertEqual(norm.kernphysik_typ, KernphysikTyp.ORDNUNGS_KERNPHYSIK)
        self.assertEqual(norm.prozedur, KernphysikProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kernphysik_weight, 0.0)

    def test_kki_kernphysik_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        feld = build_kernphysik_feld(feld_id="feld-301-expansion")
        norm = next(n for n in feld.normen if n.geltung is KernphysikGeltung.GRUNDLEGEND_KERNPHYSIKALISCH)

        self.assertEqual(norm.kernphysik_typ, KernphysikTyp.SOUVERAENITAETS_KERNPHYSIK)
        self.assertEqual(norm.prozedur, KernphysikProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_kernphysik_feld_aggregates_feld_signal(self) -> None:
        feld = build_kernphysik_feld(feld_id="feld-301-signal")

        self.assertEqual(feld.feld_signal.status, "feld-gesperrt")
        self.assertEqual(feld.gesperrt_norm_ids, ("feld-301-signal-stability-lane",))
        self.assertEqual(feld.kernphysikalisch_norm_ids, ("feld-301-signal-governance-lane",))
        self.assertEqual(feld.grundlegend_norm_ids, ("feld-301-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #302 NukleonRegister
    # ------------------------------------------------------------------

    def test_kki_nukleon_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_nukleon_register(register_id="register-302-stability")
        norm = next(n for n in register.normen if n.geltung is NukleonGeltung.GESPERRT)

        self.assertIsInstance(register, NukleonRegister)
        self.assertIsInstance(norm, NukleonNorm)
        self.assertEqual(norm.nukleon_typ, NukleonTyp.SCHUTZ_NUKLEON)
        self.assertEqual(norm.prozedur, NukleonProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.nukleon_tier, 1)

    def test_kki_nukleon_register_builds_nukleonisch_ordnungs_norm(self) -> None:
        register = build_nukleon_register(register_id="register-302-governance")
        norm = next(n for n in register.normen if n.geltung is NukleonGeltung.NUKLEONISCH)

        self.assertEqual(norm.nukleon_typ, NukleonTyp.ORDNUNGS_NUKLEON)
        self.assertEqual(norm.prozedur, NukleonProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.nukleon_weight, 0.0)

    def test_kki_nukleon_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_nukleon_register(register_id="register-302-expansion")
        norm = next(n for n in register.normen if n.geltung is NukleonGeltung.GRUNDLEGEND_NUKLEONISCH)

        self.assertEqual(norm.nukleon_typ, NukleonTyp.SOUVERAENITAETS_NUKLEON)
        self.assertEqual(norm.prozedur, NukleonProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_nukleon_register_aggregates_register_signal(self) -> None:
        register = build_nukleon_register(register_id="register-302-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-302-signal-stability-lane",))
        self.assertEqual(register.nukleonisch_norm_ids, ("register-302-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-302-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #303 StarkCharta
    # ------------------------------------------------------------------

    def test_kki_stark_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_stark_charta(charta_id="charta-303-stability")
        norm = next(n for n in charta.normen if n.geltung is StarkGeltung.GESPERRT)

        self.assertIsInstance(charta, StarkCharta)
        self.assertIsInstance(norm, StarkNorm)
        self.assertEqual(norm.stark_typ, StarkTyp.SCHUTZ_STARKRAFT)
        self.assertEqual(norm.prozedur, StarkProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.stark_tier, 1)

    def test_kki_stark_charta_builds_stark_ordnungs_norm(self) -> None:
        charta = build_stark_charta(charta_id="charta-303-governance")
        norm = next(n for n in charta.normen if n.geltung is StarkGeltung.STARK)

        self.assertEqual(norm.stark_typ, StarkTyp.ORDNUNGS_STARKRAFT)
        self.assertEqual(norm.prozedur, StarkProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.stark_weight, 0.0)

    def test_kki_stark_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_stark_charta(charta_id="charta-303-expansion")
        norm = next(n for n in charta.normen if n.geltung is StarkGeltung.GRUNDLEGEND_STARK)

        self.assertEqual(norm.stark_typ, StarkTyp.SOUVERAENITAETS_STARKRAFT)
        self.assertEqual(norm.prozedur, StarkProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_stark_charta_aggregates_charta_signal(self) -> None:
        charta = build_stark_charta(charta_id="charta-303-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-303-signal-stability-lane",))
        self.assertEqual(charta.stark_norm_ids, ("charta-303-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-303-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #304 SchwachKodex
    # ------------------------------------------------------------------

    def test_kki_schwach_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_schwach_kodex(kodex_id="kodex-304-stability")
        norm = next(n for n in kodex.normen if n.geltung is SchwachGeltung.GESPERRT)

        self.assertIsInstance(kodex, SchwachKodex)
        self.assertIsInstance(norm, SchwachNorm)
        self.assertEqual(norm.schwach_typ, SchwachTyp.SCHUTZ_SCHWACHKRAFT)
        self.assertEqual(norm.prozedur, SchwachProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.schwach_tier, 1)

    def test_kki_schwach_kodex_builds_schwach_ordnungs_norm(self) -> None:
        kodex = build_schwach_kodex(kodex_id="kodex-304-governance")
        norm = next(n for n in kodex.normen if n.geltung is SchwachGeltung.SCHWACH)

        self.assertEqual(norm.schwach_typ, SchwachTyp.ORDNUNGS_SCHWACHKRAFT)
        self.assertEqual(norm.prozedur, SchwachProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.schwach_weight, 0.0)

    def test_kki_schwach_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_schwach_kodex(kodex_id="kodex-304-expansion")
        norm = next(n for n in kodex.normen if n.geltung is SchwachGeltung.GRUNDLEGEND_SCHWACH)

        self.assertEqual(norm.schwach_typ, SchwachTyp.SOUVERAENITAETS_SCHWACHKRAFT)
        self.assertEqual(norm.prozedur, SchwachProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_schwach_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_schwach_kodex(kodex_id="kodex-304-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-304-signal-stability-lane",))
        self.assertEqual(kodex.schwach_norm_ids, ("kodex-304-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-304-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #305 KernspaltungsPakt
    # ------------------------------------------------------------------

    def test_kki_kernspaltungs_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_kernspaltungs_pakt(pakt_id="pakt-305-stability")
        norm = next(n for n in pakt.normen if n.geltung is KernspaltungsGeltung.GESPERRT)

        self.assertIsInstance(pakt, KernspaltungsPakt)
        self.assertIsInstance(norm, KernspaltungsNorm)
        self.assertEqual(norm.kernspaltungs_typ, KernspaltungsTyp.SCHUTZ_KERNSPALTUNG)
        self.assertEqual(norm.prozedur, KernspaltungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kernspaltungs_tier, 1)

    def test_kki_kernspaltungs_pakt_builds_kerngespalten_ordnungs_norm(self) -> None:
        pakt = build_kernspaltungs_pakt(pakt_id="pakt-305-governance")
        norm = next(n for n in pakt.normen if n.geltung is KernspaltungsGeltung.KERNGESPALTEN)

        self.assertEqual(norm.kernspaltungs_typ, KernspaltungsTyp.ORDNUNGS_KERNSPALTUNG)
        self.assertEqual(norm.prozedur, KernspaltungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kernspaltungs_weight, 0.0)

    def test_kki_kernspaltungs_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_kernspaltungs_pakt(pakt_id="pakt-305-expansion")
        norm = next(n for n in pakt.normen if n.geltung is KernspaltungsGeltung.GRUNDLEGEND_KERNGESPALTEN)

        self.assertEqual(norm.kernspaltungs_typ, KernspaltungsTyp.SOUVERAENITAETS_KERNSPALTUNG)
        self.assertEqual(norm.prozedur, KernspaltungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_kernspaltungs_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_kernspaltungs_pakt(pakt_id="pakt-305-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-305-signal-stability-lane",))
        self.assertEqual(pakt.kerngespalten_norm_ids, ("pakt-305-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-305-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #306 KernfusionsManifest
    # ------------------------------------------------------------------

    def test_kki_kernfusions_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_kernfusions_manifest(manifest_id="manifest-306-stability")
        norm = next(n for n in manifest.normen if n.geltung is KernfusionsGeltung.GESPERRT)

        self.assertIsInstance(manifest, KernfusionsManifest)
        self.assertIsInstance(norm, KernfusionsNorm)
        self.assertEqual(norm.kernfusions_typ, KernfusionsTyp.SCHUTZ_KERNFUSION)
        self.assertEqual(norm.prozedur, KernfusionsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kernfusions_tier, 1)

    def test_kki_kernfusions_manifest_builds_kernverschmolzen_ordnungs_norm(self) -> None:
        manifest = build_kernfusions_manifest(manifest_id="manifest-306-governance")
        norm = next(n for n in manifest.normen if n.geltung is KernfusionsGeltung.KERNVERSCHMOLZEN)

        self.assertEqual(norm.kernfusions_typ, KernfusionsTyp.ORDNUNGS_KERNFUSION)
        self.assertEqual(norm.prozedur, KernfusionsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kernfusions_weight, 0.0)

    def test_kki_kernfusions_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_kernfusions_manifest(manifest_id="manifest-306-expansion")
        norm = next(n for n in manifest.normen if n.geltung is KernfusionsGeltung.GRUNDLEGEND_KERNVERSCHMOLZEN)

        self.assertEqual(norm.kernfusions_typ, KernfusionsTyp.SOUVERAENITAETS_KERNFUSION)
        self.assertEqual(norm.prozedur, KernfusionsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_kernfusions_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_kernfusions_manifest(manifest_id="manifest-306-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-306-signal-stability-lane",))
        self.assertEqual(manifest.kernverschmolzen_norm_ids, ("manifest-306-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-306-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #307 RadioaktivitaetsSenat
    # ------------------------------------------------------------------

    def test_kki_radioaktivitaets_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_radioaktivitaets_senat(senat_id="senat-307-stability")
        norm = next(n for n in senat.normen if n.geltung is RadioaktivitaetsGeltung.GESPERRT)

        self.assertIsInstance(senat, RadioaktivitaetsSenat)
        self.assertIsInstance(norm, RadioaktivitaetsNorm)
        self.assertEqual(norm.radioaktivitaets_typ, RadioaktivitaetsTyp.SCHUTZ_RADIOAKTIVITAET)
        self.assertEqual(norm.prozedur, RadioaktivitaetsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.radioaktivitaets_tier, 1)

    def test_kki_radioaktivitaets_senat_builds_radioaktiv_ordnungs_norm(self) -> None:
        senat = build_radioaktivitaets_senat(senat_id="senat-307-governance")
        norm = next(n for n in senat.normen if n.geltung is RadioaktivitaetsGeltung.RADIOAKTIV)

        self.assertEqual(norm.radioaktivitaets_typ, RadioaktivitaetsTyp.ORDNUNGS_RADIOAKTIVITAET)
        self.assertEqual(norm.prozedur, RadioaktivitaetsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.radioaktivitaets_weight, 0.0)

    def test_kki_radioaktivitaets_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_radioaktivitaets_senat(senat_id="senat-307-expansion")
        norm = next(n for n in senat.normen if n.geltung is RadioaktivitaetsGeltung.GRUNDLEGEND_RADIOAKTIV)

        self.assertEqual(norm.radioaktivitaets_typ, RadioaktivitaetsTyp.SOUVERAENITAETS_RADIOAKTIVITAET)
        self.assertEqual(norm.prozedur, RadioaktivitaetsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_radioaktivitaets_senat_aggregates_senat_signal(self) -> None:
        senat = build_radioaktivitaets_senat(senat_id="senat-307-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-307-signal-stability-lane",))
        self.assertEqual(senat.radioaktiv_norm_ids, ("senat-307-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-307-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #308 ZerfallsNorm  (*_norm pattern)
    # ------------------------------------------------------------------

    def test_kki_zerfalls_norm_builds_gesperrt_schutz_eintrag(self) -> None:
        satz = build_zerfalls_norm(norm_id="zerfalls-norm-308-stability")
        eintrag = next(n for n in satz.normen if n.geltung is ZerfallsNormGeltung.GESPERRT)

        self.assertIsInstance(satz, ZerfallsNormSatz)
        self.assertIsInstance(eintrag, ZerfallsNormEintrag)
        self.assertEqual(eintrag.zerfalls_norm_typ, ZerfallsNormTyp.SCHUTZ_ZERFALL)
        self.assertEqual(eintrag.prozedur, ZerfallsNormProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.zerfalls_norm_tier, 1)

    def test_kki_zerfalls_norm_builds_zerfallen_ordnungs_eintrag(self) -> None:
        satz = build_zerfalls_norm(norm_id="zerfalls-norm-308-governance")
        eintrag = next(n for n in satz.normen if n.geltung is ZerfallsNormGeltung.ZERFALLEN)

        self.assertEqual(eintrag.zerfalls_norm_typ, ZerfallsNormTyp.ORDNUNGS_ZERFALL)
        self.assertEqual(eintrag.prozedur, ZerfallsNormProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.zerfalls_norm_weight, 0.0)

    def test_kki_zerfalls_norm_builds_grundlegend_souveraenitaets_eintrag(self) -> None:
        satz = build_zerfalls_norm(norm_id="zerfalls-norm-308-expansion")
        eintrag = next(n for n in satz.normen if n.geltung is ZerfallsNormGeltung.GRUNDLEGEND_ZERFALLEN)

        self.assertEqual(eintrag.zerfalls_norm_typ, ZerfallsNormTyp.SOUVERAENITAETS_ZERFALL)
        self.assertEqual(eintrag.prozedur, ZerfallsNormProzedur.PLENARPROTOKOLL)
        self.assertTrue(eintrag.canonical)

    def test_kki_zerfalls_norm_aggregates_norm_signal(self) -> None:
        satz = build_zerfalls_norm(norm_id="zerfalls-norm-308-signal")

        self.assertEqual(satz.norm_signal.status, "norm-gesperrt")
        self.assertEqual(satz.gesperrt_norm_ids, ("zerfalls-norm-308-signal-stability-lane",))
        self.assertEqual(satz.zerfallen_norm_ids, ("zerfalls-norm-308-signal-governance-lane",))
        self.assertEqual(satz.grundlegend_norm_ids, ("zerfalls-norm-308-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #309 NuklearCharta
    # ------------------------------------------------------------------

    def test_kki_nuklear_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_nuklear_charta(charta_id="charta-309-stability")
        norm = next(n for n in charta.normen if n.geltung is NuklearChartaGeltung.GESPERRT)

        self.assertIsInstance(charta, NuklearCharta)
        self.assertIsInstance(norm, NuklearChartaNorm)
        self.assertEqual(norm.nuklear_charta_typ, NuklearChartaTyp.SCHUTZ_NUKLEARSTRUKTUR)
        self.assertEqual(norm.prozedur, NuklearChartaProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.nuklear_charta_tier, 1)

    def test_kki_nuklear_charta_builds_nuklearchartiert_ordnungs_norm(self) -> None:
        charta = build_nuklear_charta(charta_id="charta-309-governance")
        norm = next(n for n in charta.normen if n.geltung is NuklearChartaGeltung.NUKLEARCHARTIERT)

        self.assertEqual(norm.nuklear_charta_typ, NuklearChartaTyp.ORDNUNGS_NUKLEARSTRUKTUR)
        self.assertEqual(norm.prozedur, NuklearChartaProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.nuklear_charta_weight, 0.0)

    def test_kki_nuklear_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_nuklear_charta(charta_id="charta-309-expansion")
        norm = next(n for n in charta.normen if n.geltung is NuklearChartaGeltung.GRUNDLEGEND_NUKLEARCHARTIERT)

        self.assertEqual(norm.nuklear_charta_typ, NuklearChartaTyp.SOUVERAENITAETS_NUKLEARSTRUKTUR)
        self.assertEqual(norm.prozedur, NuklearChartaProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_nuklear_charta_aggregates_charta_signal(self) -> None:
        charta = build_nuklear_charta(charta_id="charta-309-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-309-signal-stability-lane",))
        self.assertEqual(charta.nuklearchartiert_norm_ids, ("charta-309-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-309-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #310 KernphysikVerfassung  (Block-Krone)
    # ------------------------------------------------------------------

    def test_kki_kernphysik_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_kernphysik_verfassung(verfassung_id="verfassung-310-stability")
        norm = next(n for n in verfassung.normen if n.geltung is KernphysikVerfassungsGeltung.GESPERRT)

        self.assertIsInstance(verfassung, KernphysikVerfassung)
        self.assertIsInstance(norm, KernphysikVerfassungsNorm)
        self.assertEqual(norm.kernphysikverfassungs_typ, KernphysikVerfassungsTyp.SCHUTZ_KERNPHYSIKVERFASSUNG)
        self.assertEqual(norm.prozedur, KernphysikVerfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kernphysikverfassungs_tier, 1)

    def test_kki_kernphysik_verfassung_builds_kernphysikverfasst_ordnungs_norm(self) -> None:
        verfassung = build_kernphysik_verfassung(verfassung_id="verfassung-310-governance")
        norm = next(n for n in verfassung.normen if n.geltung is KernphysikVerfassungsGeltung.KERNPHYSIKVERFASST)

        self.assertEqual(norm.kernphysikverfassungs_typ, KernphysikVerfassungsTyp.ORDNUNGS_KERNPHYSIKVERFASSUNG)
        self.assertEqual(norm.prozedur, KernphysikVerfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kernphysikverfassungs_weight, 0.0)

    def test_kki_kernphysik_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_kernphysik_verfassung(verfassung_id="verfassung-310-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is KernphysikVerfassungsGeltung.GRUNDLEGEND_KERNPHYSIKVERFASST)

        self.assertEqual(norm.kernphysikverfassungs_typ, KernphysikVerfassungsTyp.SOUVERAENITAETS_KERNPHYSIKVERFASSUNG)
        self.assertEqual(norm.prozedur, KernphysikVerfassungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_kernphysik_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_kernphysik_verfassung(verfassung_id="verfassung-310-signal")

        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-310-signal-stability-lane",))
        self.assertEqual(verfassung.kernphysikverfasst_norm_ids, ("verfassung-310-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-310-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #311 TeilchenFeld
    # ------------------------------------------------------------------

    def test_kki_teilchen_feld_builds_gesperrt_schutz_norm(self) -> None:
        feld = build_teilchen_feld(feld_id="feld-311-stability")
        norm = next(n for n in feld.normen if n.geltung is TeilchenGeltung.GESPERRT)

        self.assertIsInstance(feld, TeilchenFeld)
        self.assertIsInstance(norm, TeilchenNorm)
        self.assertEqual(norm.teilchen_typ, TeilchenTyp.SCHUTZ_TEILCHEN)
        self.assertEqual(norm.prozedur, TeilchenProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.teilchen_tier, 1)

    def test_kki_teilchen_feld_builds_teilchengebunden_ordnungs_norm(self) -> None:
        feld = build_teilchen_feld(feld_id="feld-311-governance")
        norm = next(n for n in feld.normen if n.geltung is TeilchenGeltung.TEILCHENGEBUNDEN)

        self.assertEqual(norm.teilchen_typ, TeilchenTyp.ORDNUNGS_TEILCHEN)
        self.assertEqual(norm.prozedur, TeilchenProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.teilchen_weight, 0.0)

    def test_kki_teilchen_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        feld = build_teilchen_feld(feld_id="feld-311-expansion")
        norm = next(n for n in feld.normen if n.geltung is TeilchenGeltung.GRUNDLEGEND_TEILCHENGEBUNDEN)

        self.assertEqual(norm.teilchen_typ, TeilchenTyp.SOUVERAENITAETS_TEILCHEN)
        self.assertEqual(norm.prozedur, TeilchenProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_teilchen_feld_aggregates_feld_signal(self) -> None:
        feld = build_teilchen_feld(feld_id="feld-311-signal")

        self.assertEqual(feld.feld_signal.status, "feld-gesperrt")
        self.assertEqual(feld.gesperrt_norm_ids, ("feld-311-signal-stability-lane",))
        self.assertEqual(feld.teilchengebunden_norm_ids, ("feld-311-signal-governance-lane",))
        self.assertEqual(feld.grundlegend_norm_ids, ("feld-311-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #312 QuarkRegister
    # ------------------------------------------------------------------

    def test_kki_quark_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_quark_register(register_id="register-312-stability")
        norm = next(n for n in register.normen if n.geltung is QuarkGeltung.GESPERRT)

        self.assertIsInstance(register, QuarkRegister)
        self.assertIsInstance(norm, QuarkNorm)
        self.assertEqual(norm.quark_typ, QuarkTyp.SCHUTZ_QUARK)
        self.assertEqual(norm.prozedur, QuarkProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.quark_tier, 1)

    def test_kki_quark_register_builds_quarkgebunden_ordnungs_norm(self) -> None:
        register = build_quark_register(register_id="register-312-governance")
        norm = next(n for n in register.normen if n.geltung is QuarkGeltung.QUARKGEBUNDEN)

        self.assertEqual(norm.quark_typ, QuarkTyp.ORDNUNGS_QUARK)
        self.assertEqual(norm.prozedur, QuarkProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.quark_weight, 0.0)

    def test_kki_quark_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_quark_register(register_id="register-312-expansion")
        norm = next(n for n in register.normen if n.geltung is QuarkGeltung.GRUNDLEGEND_QUARKGEBUNDEN)

        self.assertEqual(norm.quark_typ, QuarkTyp.SOUVERAENITAETS_QUARK)
        self.assertEqual(norm.prozedur, QuarkProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_quark_register_aggregates_register_signal(self) -> None:
        register = build_quark_register(register_id="register-312-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-312-signal-stability-lane",))
        self.assertEqual(register.quarkgebunden_norm_ids, ("register-312-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-312-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #313 LeptonCharta
    # ------------------------------------------------------------------

    def test_kki_lepton_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_lepton_charta(charta_id="charta-313-stability")
        norm = next(n for n in charta.normen if n.geltung is LeptonGeltung.GESPERRT)

        self.assertIsInstance(charta, LeptonCharta)
        self.assertIsInstance(norm, LeptonNorm)
        self.assertEqual(norm.lepton_typ, LeptonTyp.SCHUTZ_LEPTON)
        self.assertEqual(norm.prozedur, LeptonProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.lepton_tier, 1)

    def test_kki_lepton_charta_builds_leptonisch_ordnungs_norm(self) -> None:
        charta = build_lepton_charta(charta_id="charta-313-governance")
        norm = next(n for n in charta.normen if n.geltung is LeptonGeltung.LEPTONISCH)

        self.assertEqual(norm.lepton_typ, LeptonTyp.ORDNUNGS_LEPTON)
        self.assertEqual(norm.prozedur, LeptonProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.lepton_weight, 0.0)

    def test_kki_lepton_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_lepton_charta(charta_id="charta-313-expansion")
        norm = next(n for n in charta.normen if n.geltung is LeptonGeltung.GRUNDLEGEND_LEPTONISCH)

        self.assertEqual(norm.lepton_typ, LeptonTyp.SOUVERAENITAETS_LEPTON)
        self.assertEqual(norm.prozedur, LeptonProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_lepton_charta_aggregates_charta_signal(self) -> None:
        charta = build_lepton_charta(charta_id="charta-313-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-313-signal-stability-lane",))
        self.assertEqual(charta.leptonisch_norm_ids, ("charta-313-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-313-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #314 GluonKodex
    # ------------------------------------------------------------------

    def test_kki_gluon_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_gluon_kodex(kodex_id="kodex-314-stability")
        norm = next(n for n in kodex.normen if n.geltung is GluonGeltung.GESPERRT)

        self.assertIsInstance(kodex, GluonKodex)
        self.assertIsInstance(norm, GluonNorm)
        self.assertEqual(norm.gluon_typ, GluonTyp.SCHUTZ_GLUON)
        self.assertEqual(norm.prozedur, GluonProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.gluon_tier, 1)

    def test_kki_gluon_kodex_builds_gluonisch_ordnungs_norm(self) -> None:
        kodex = build_gluon_kodex(kodex_id="kodex-314-governance")
        norm = next(n for n in kodex.normen if n.geltung is GluonGeltung.GLUONISCH)

        self.assertEqual(norm.gluon_typ, GluonTyp.ORDNUNGS_GLUON)
        self.assertEqual(norm.prozedur, GluonProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.gluon_weight, 0.0)

    def test_kki_gluon_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_gluon_kodex(kodex_id="kodex-314-expansion")
        norm = next(n for n in kodex.normen if n.geltung is GluonGeltung.GRUNDLEGEND_GLUONISCH)

        self.assertEqual(norm.gluon_typ, GluonTyp.SOUVERAENITAETS_GLUON)
        self.assertEqual(norm.prozedur, GluonProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_gluon_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_gluon_kodex(kodex_id="kodex-314-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-314-signal-stability-lane",))
        self.assertEqual(kodex.gluonisch_norm_ids, ("kodex-314-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-314-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #315 EichbosonPakt
    # ------------------------------------------------------------------

    def test_kki_eichboson_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_eichboson_pakt(pakt_id="pakt-315-stability")
        norm = next(n for n in pakt.normen if n.geltung is EichbosonGeltung.GESPERRT)

        self.assertIsInstance(pakt, EichbosonPakt)
        self.assertIsInstance(norm, EichbosonNorm)
        self.assertEqual(norm.eichboson_typ, EichbosonTyp.SCHUTZ_EICHBOSON)
        self.assertEqual(norm.prozedur, EichbosonProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.eichboson_tier, 1)

    def test_kki_eichboson_pakt_builds_eichbosonal_ordnungs_norm(self) -> None:
        pakt = build_eichboson_pakt(pakt_id="pakt-315-governance")
        norm = next(n for n in pakt.normen if n.geltung is EichbosonGeltung.EICHBOSONAL)

        self.assertEqual(norm.eichboson_typ, EichbosonTyp.ORDNUNGS_EICHBOSON)
        self.assertEqual(norm.prozedur, EichbosonProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.eichboson_weight, 0.0)

    def test_kki_eichboson_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_eichboson_pakt(pakt_id="pakt-315-expansion")
        norm = next(n for n in pakt.normen if n.geltung is EichbosonGeltung.GRUNDLEGEND_EICHBOSONAL)

        self.assertEqual(norm.eichboson_typ, EichbosonTyp.SOUVERAENITAETS_EICHBOSON)
        self.assertEqual(norm.prozedur, EichbosonProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_eichboson_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_eichboson_pakt(pakt_id="pakt-315-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-315-signal-stability-lane",))
        self.assertEqual(pakt.eichbosonal_norm_ids, ("pakt-315-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-315-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #316 HiggsManifest
    # ------------------------------------------------------------------

    def test_kki_higgs_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_higgs_manifest(manifest_id="manifest-316-stability")
        norm = next(n for n in manifest.normen if n.geltung is HiggsGeltung.GESPERRT)

        self.assertIsInstance(manifest, HiggsManifest)
        self.assertIsInstance(norm, HiggsNorm)
        self.assertEqual(norm.higgs_typ, HiggsTyp.SCHUTZ_HIGGS)
        self.assertEqual(norm.prozedur, HiggsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.higgs_tier, 1)

    def test_kki_higgs_manifest_builds_higgsgekoppelt_ordnungs_norm(self) -> None:
        manifest = build_higgs_manifest(manifest_id="manifest-316-governance")
        norm = next(n for n in manifest.normen if n.geltung is HiggsGeltung.HIGGSGEKOPPELT)

        self.assertEqual(norm.higgs_typ, HiggsTyp.ORDNUNGS_HIGGS)
        self.assertEqual(norm.prozedur, HiggsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.higgs_weight, 0.0)

    def test_kki_higgs_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_higgs_manifest(manifest_id="manifest-316-expansion")
        norm = next(n for n in manifest.normen if n.geltung is HiggsGeltung.GRUNDLEGEND_HIGGSGEKOPPELT)

        self.assertEqual(norm.higgs_typ, HiggsTyp.SOUVERAENITAETS_HIGGS)
        self.assertEqual(norm.prozedur, HiggsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_higgs_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_higgs_manifest(manifest_id="manifest-316-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-316-signal-stability-lane",))
        self.assertEqual(manifest.higgsgekoppelt_norm_ids, ("manifest-316-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-316-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #317 SymmetriebrechungsSenat
    # ------------------------------------------------------------------

    def test_kki_symmetriebrechungs_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_symmetriebrechungs_senat(senat_id="senat-317-stability")
        norm = next(n for n in senat.normen if n.geltung is SymmetriebrechungsGeltung.GESPERRT)

        self.assertIsInstance(senat, SymmetriebrechungsSenat)
        self.assertIsInstance(norm, SymmetriebrechungsNorm)
        self.assertEqual(norm.symmetriebrechungs_typ, SymmetriebrechungsTyp.SCHUTZ_SYMMETRIEBRECHUNG)
        self.assertEqual(norm.prozedur, SymmetriebrechungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.symmetriebrechungs_tier, 1)

    def test_kki_symmetriebrechungs_senat_builds_symmetriegebrochen_ordnungs_norm(self) -> None:
        senat = build_symmetriebrechungs_senat(senat_id="senat-317-governance")
        norm = next(n for n in senat.normen if n.geltung is SymmetriebrechungsGeltung.SYMMETRIEGEBROCHEN)

        self.assertEqual(norm.symmetriebrechungs_typ, SymmetriebrechungsTyp.ORDNUNGS_SYMMETRIEBRECHUNG)
        self.assertEqual(norm.prozedur, SymmetriebrechungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.symmetriebrechungs_weight, 0.0)

    def test_kki_symmetriebrechungs_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_symmetriebrechungs_senat(senat_id="senat-317-expansion")
        norm = next(n for n in senat.normen if n.geltung is SymmetriebrechungsGeltung.GRUNDLEGEND_SYMMETRIEGEBROCHEN)

        self.assertEqual(norm.symmetriebrechungs_typ, SymmetriebrechungsTyp.SOUVERAENITAETS_SYMMETRIEBRECHUNG)
        self.assertEqual(norm.prozedur, SymmetriebrechungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_symmetriebrechungs_senat_aggregates_senat_signal(self) -> None:
        senat = build_symmetriebrechungs_senat(senat_id="senat-317-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-317-signal-stability-lane",))
        self.assertEqual(senat.symmetriegebrochen_norm_ids, ("senat-317-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-317-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #318 FeynmanNorm  (*_norm pattern)
    # ------------------------------------------------------------------

    def test_kki_feynman_norm_builds_gesperrt_schutz_eintrag(self) -> None:
        satz = build_feynman_norm(norm_id="feynman-norm-318-stability")
        eintrag = next(n for n in satz.normen if n.geltung is FeynmanNormGeltung.GESPERRT)

        self.assertIsInstance(satz, FeynmanNormSatz)
        self.assertIsInstance(eintrag, FeynmanNormEintrag)
        self.assertEqual(eintrag.feynman_norm_typ, FeynmanNormTyp.SCHUTZ_FEYNMAN)
        self.assertEqual(eintrag.prozedur, FeynmanNormProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.feynman_norm_tier, 1)

    def test_kki_feynman_norm_builds_feynmandiagrammiert_ordnungs_eintrag(self) -> None:
        satz = build_feynman_norm(norm_id="feynman-norm-318-governance")
        eintrag = next(n for n in satz.normen if n.geltung is FeynmanNormGeltung.FEYNMANDIAGRAMMIERT)

        self.assertEqual(eintrag.feynman_norm_typ, FeynmanNormTyp.ORDNUNGS_FEYNMAN)
        self.assertEqual(eintrag.prozedur, FeynmanNormProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.feynman_norm_weight, 0.0)

    def test_kki_feynman_norm_builds_grundlegend_souveraenitaets_eintrag(self) -> None:
        satz = build_feynman_norm(norm_id="feynman-norm-318-expansion")
        eintrag = next(n for n in satz.normen if n.geltung is FeynmanNormGeltung.GRUNDLEGEND_FEYNMANDIAGRAMMIERT)

        self.assertEqual(eintrag.feynman_norm_typ, FeynmanNormTyp.SOUVERAENITAETS_FEYNMAN)
        self.assertEqual(eintrag.prozedur, FeynmanNormProzedur.PLENARPROTOKOLL)
        self.assertTrue(eintrag.canonical)

    def test_kki_feynman_norm_aggregates_norm_signal(self) -> None:
        satz = build_feynman_norm(norm_id="feynman-norm-318-signal")

        self.assertEqual(satz.norm_signal.status, "norm-gesperrt")
        self.assertEqual(satz.gesperrt_norm_ids, ("feynman-norm-318-signal-stability-lane",))
        self.assertEqual(satz.feynmandiagrammiert_norm_ids, ("feynman-norm-318-signal-governance-lane",))
        self.assertEqual(satz.grundlegend_norm_ids, ("feynman-norm-318-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #319 StandardmodellCharta
    # ------------------------------------------------------------------

    def test_kki_standardmodell_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_standardmodell_charta(charta_id="charta-319-stability")
        norm = next(n for n in charta.normen if n.geltung is StandardmodellGeltung.GESPERRT)

        self.assertIsInstance(charta, StandardmodellCharta)
        self.assertIsInstance(norm, StandardmodellNorm)
        self.assertEqual(norm.standardmodell_typ, StandardmodellTyp.SCHUTZ_STANDARDMODELL)
        self.assertEqual(norm.prozedur, StandardmodellProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.standardmodell_tier, 1)

    def test_kki_standardmodell_charta_builds_standardmodelliert_ordnungs_norm(self) -> None:
        charta = build_standardmodell_charta(charta_id="charta-319-governance")
        norm = next(n for n in charta.normen if n.geltung is StandardmodellGeltung.STANDARDMODELLIERT)

        self.assertEqual(norm.standardmodell_typ, StandardmodellTyp.ORDNUNGS_STANDARDMODELL)
        self.assertEqual(norm.prozedur, StandardmodellProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.standardmodell_weight, 0.0)

    def test_kki_standardmodell_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_standardmodell_charta(charta_id="charta-319-expansion")
        norm = next(n for n in charta.normen if n.geltung is StandardmodellGeltung.GRUNDLEGEND_STANDARDMODELLIERT)

        self.assertEqual(norm.standardmodell_typ, StandardmodellTyp.SOUVERAENITAETS_STANDARDMODELL)
        self.assertEqual(norm.prozedur, StandardmodellProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_standardmodell_charta_aggregates_charta_signal(self) -> None:
        charta = build_standardmodell_charta(charta_id="charta-319-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-319-signal-stability-lane",))
        self.assertEqual(charta.standardmodelliert_norm_ids, ("charta-319-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-319-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #320 TeilchenphysikVerfassung  (Block-Krone)
    # ------------------------------------------------------------------

    def test_kki_teilchenphysik_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_teilchenphysik_verfassung(verfassung_id="verfassung-320-stability")
        norm = next(n for n in verfassung.normen if n.geltung is TeilchenphysikGeltung.GESPERRT)

        self.assertIsInstance(verfassung, TeilchenphysikVerfassung)
        self.assertIsInstance(norm, TeilchenphysikNorm)
        self.assertEqual(norm.teilchenphysik_typ, TeilchenphysikTyp.SCHUTZ_TEILCHENPHYSIK)
        self.assertEqual(norm.prozedur, TeilchenphysikProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.teilchenphysik_tier, 1)

    def test_kki_teilchenphysik_verfassung_builds_teilchenphysikverfasst_ordnungs_norm(self) -> None:
        verfassung = build_teilchenphysik_verfassung(verfassung_id="verfassung-320-governance")
        norm = next(n for n in verfassung.normen if n.geltung is TeilchenphysikGeltung.TEILCHENPHYSIKVERFASST)

        self.assertEqual(norm.teilchenphysik_typ, TeilchenphysikTyp.ORDNUNGS_TEILCHENPHYSIK)
        self.assertEqual(norm.prozedur, TeilchenphysikProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.teilchenphysik_weight, 0.0)

    def test_kki_teilchenphysik_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_teilchenphysik_verfassung(verfassung_id="verfassung-320-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is TeilchenphysikGeltung.GRUNDLEGEND_TEILCHENPHYSIKVERFASST)

        self.assertEqual(norm.teilchenphysik_typ, TeilchenphysikTyp.SOUVERAENITAETS_TEILCHENPHYSIK)
        self.assertEqual(norm.prozedur, TeilchenphysikProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_teilchenphysik_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_teilchenphysik_verfassung(verfassung_id="verfassung-320-signal")

        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-320-signal-stability-lane",))
        self.assertEqual(verfassung.teilchenphysikverfasst_norm_ids, ("verfassung-320-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-320-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #321 KosmologieFeld
    # ------------------------------------------------------------------

    def test_kki_kosmologie_feld_builds_gesperrt_schutz_norm(self) -> None:
        feld = build_kosmologie_feld(feld_id="feld-321-stability")
        norm = next(n for n in feld.normen if n.geltung is KosmologieGeltung.GESPERRT)

        self.assertIsInstance(feld, KosmologieFeld)
        self.assertIsInstance(norm, KosmologieNorm)
        self.assertEqual(norm.kosmologie_typ, KosmologieTyp.SCHUTZ_KOSMOLOGIE)
        self.assertEqual(norm.prozedur, KosmologieProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kosmologie_tier, 1)

    def test_kki_kosmologie_feld_builds_kosmologisch_ordnungs_norm(self) -> None:
        feld = build_kosmologie_feld(feld_id="feld-321-governance")
        norm = next(n for n in feld.normen if n.geltung is KosmologieGeltung.KOSMOLOGISCH)

        self.assertEqual(norm.kosmologie_typ, KosmologieTyp.ORDNUNGS_KOSMOLOGIE)
        self.assertEqual(norm.prozedur, KosmologieProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kosmologie_weight, 0.0)

    def test_kki_kosmologie_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        feld = build_kosmologie_feld(feld_id="feld-321-expansion")
        norm = next(n for n in feld.normen if n.geltung is KosmologieGeltung.GRUNDLEGEND_KOSMOLOGISCH)

        self.assertEqual(norm.kosmologie_typ, KosmologieTyp.SOUVERAENITAETS_KOSMOLOGIE)
        self.assertEqual(norm.prozedur, KosmologieProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_kosmologie_feld_aggregates_feld_signal(self) -> None:
        feld = build_kosmologie_feld(feld_id="feld-321-signal")

        self.assertEqual(feld.feld_signal.status, "feld-gesperrt")
        self.assertEqual(feld.gesperrt_norm_ids, ("feld-321-signal-stability-lane",))
        self.assertEqual(feld.kosmologisch_norm_ids, ("feld-321-signal-governance-lane",))
        self.assertEqual(feld.grundlegend_norm_ids, ("feld-321-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #322 UrknallRegister
    # ------------------------------------------------------------------

    def test_kki_urknall_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_urknall_register(register_id="register-322-stability")
        norm = next(n for n in register.normen if n.geltung is UrknallGeltung.GESPERRT)

        self.assertIsInstance(register, UrknallRegister)
        self.assertIsInstance(norm, UrknallNorm)
        self.assertEqual(norm.urknall_typ, UrknallTyp.SCHUTZ_URKNALL)
        self.assertEqual(norm.prozedur, UrknallProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.urknall_tier, 1)

    def test_kki_urknall_register_builds_urknallgebunden_ordnungs_norm(self) -> None:
        register = build_urknall_register(register_id="register-322-governance")
        norm = next(n for n in register.normen if n.geltung is UrknallGeltung.URKNALLGEBUNDEN)

        self.assertEqual(norm.urknall_typ, UrknallTyp.ORDNUNGS_URKNALL)
        self.assertEqual(norm.prozedur, UrknallProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.urknall_weight, 0.0)

    def test_kki_urknall_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_urknall_register(register_id="register-322-expansion")
        norm = next(n for n in register.normen if n.geltung is UrknallGeltung.GRUNDLEGEND_URKNALLGEBUNDEN)

        self.assertEqual(norm.urknall_typ, UrknallTyp.SOUVERAENITAETS_URKNALL)
        self.assertEqual(norm.prozedur, UrknallProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_urknall_register_aggregates_register_signal(self) -> None:
        register = build_urknall_register(register_id="register-322-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-322-signal-stability-lane",))
        self.assertEqual(register.urknallgebunden_norm_ids, ("register-322-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-322-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #323 InflationCharta
    # ------------------------------------------------------------------

    def test_kki_inflation_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_inflation_charta(charta_id="charta-323-stability")
        norm = next(n for n in charta.normen if n.geltung is InflationGeltung.GESPERRT)

        self.assertIsInstance(charta, InflationCharta)
        self.assertIsInstance(norm, InflationNorm)
        self.assertEqual(norm.inflation_typ, InflationTyp.SCHUTZ_INFLATION)
        self.assertEqual(norm.prozedur, InflationProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.inflation_tier, 1)

    def test_kki_inflation_charta_builds_inflationaer_ordnungs_norm(self) -> None:
        charta = build_inflation_charta(charta_id="charta-323-governance")
        norm = next(n for n in charta.normen if n.geltung is InflationGeltung.INFLATIONAER)

        self.assertEqual(norm.inflation_typ, InflationTyp.ORDNUNGS_INFLATION)
        self.assertEqual(norm.prozedur, InflationProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.inflation_weight, 0.0)

    def test_kki_inflation_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_inflation_charta(charta_id="charta-323-expansion")
        norm = next(n for n in charta.normen if n.geltung is InflationGeltung.GRUNDLEGEND_INFLATIONAER)

        self.assertEqual(norm.inflation_typ, InflationTyp.SOUVERAENITAETS_INFLATION)
        self.assertEqual(norm.prozedur, InflationProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_inflation_charta_aggregates_charta_signal(self) -> None:
        charta = build_inflation_charta(charta_id="charta-323-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-323-signal-stability-lane",))
        self.assertEqual(charta.inflationaer_norm_ids, ("charta-323-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-323-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #324 DunkleMaterieKodex
    # ------------------------------------------------------------------

    def test_kki_dunkle_materie_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_dunkle_materie_kodex(kodex_id="kodex-324-stability")
        norm = next(n for n in kodex.normen if n.geltung is DunkleMaterieGeltung.GESPERRT)

        self.assertIsInstance(kodex, DunkleMaterieKodex)
        self.assertIsInstance(norm, DunkleMaterieNorm)
        self.assertEqual(norm.dunkle_materie_typ, DunkleMaterieTyp.SCHUTZ_DUNKLE_MATERIE)
        self.assertEqual(norm.prozedur, DunkleMaterieProzedue.NOTPROZEDUR)
        self.assertGreaterEqual(norm.dunkle_materie_tier, 1)

    def test_kki_dunkle_materie_kodex_builds_dunkelmateriell_ordnungs_norm(self) -> None:
        kodex = build_dunkle_materie_kodex(kodex_id="kodex-324-governance")
        norm = next(n for n in kodex.normen if n.geltung is DunkleMaterieGeltung.DUNKELMATERIELL)

        self.assertEqual(norm.dunkle_materie_typ, DunkleMaterieTyp.ORDNUNGS_DUNKLE_MATERIE)
        self.assertEqual(norm.prozedur, DunkleMaterieProzedue.REGELPROTOKOLL)
        self.assertGreater(norm.dunkle_materie_weight, 0.0)

    def test_kki_dunkle_materie_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_dunkle_materie_kodex(kodex_id="kodex-324-expansion")
        norm = next(n for n in kodex.normen if n.geltung is DunkleMaterieGeltung.GRUNDLEGEND_DUNKELMATERIELL)

        self.assertEqual(norm.dunkle_materie_typ, DunkleMaterieTyp.SOUVERAENITAETS_DUNKLE_MATERIE)
        self.assertEqual(norm.prozedur, DunkleMaterieProzedue.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_dunkle_materie_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_dunkle_materie_kodex(kodex_id="kodex-324-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-324-signal-stability-lane",))
        self.assertEqual(kodex.dunkelmateriell_norm_ids, ("kodex-324-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-324-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #325 DunkleEnergiePakt
    # ------------------------------------------------------------------

    def test_kki_dunkle_energie_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_dunkle_energie_pakt(pakt_id="pakt-325-stability")
        norm = next(n for n in pakt.normen if n.geltung is DunkleEnergieGeltung.GESPERRT)

        self.assertIsInstance(pakt, DunkleEnergiePakt)
        self.assertIsInstance(norm, DunkleEnergieNorm)
        self.assertEqual(norm.dunkle_energie_typ, DunkleEnergieTyp.SCHUTZ_DUNKLE_ENERGIE)
        self.assertEqual(norm.prozedur, DunkleEnergieProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.dunkle_energie_tier, 1)

    def test_kki_dunkle_energie_pakt_builds_dunkelenergisch_ordnungs_norm(self) -> None:
        pakt = build_dunkle_energie_pakt(pakt_id="pakt-325-governance")
        norm = next(n for n in pakt.normen if n.geltung is DunkleEnergieGeltung.DUNKELENERGISCH)

        self.assertEqual(norm.dunkle_energie_typ, DunkleEnergieTyp.ORDNUNGS_DUNKLE_ENERGIE)
        self.assertEqual(norm.prozedur, DunkleEnergieProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.dunkle_energie_weight, 0.0)

    def test_kki_dunkle_energie_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_dunkle_energie_pakt(pakt_id="pakt-325-expansion")
        norm = next(n for n in pakt.normen if n.geltung is DunkleEnergieGeltung.GRUNDLEGEND_DUNKELENERGISCH)

        self.assertEqual(norm.dunkle_energie_typ, DunkleEnergieTyp.SOUVERAENITAETS_DUNKLE_ENERGIE)
        self.assertEqual(norm.prozedur, DunkleEnergieProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_dunkle_energie_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_dunkle_energie_pakt(pakt_id="pakt-325-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-325-signal-stability-lane",))
        self.assertEqual(pakt.dunkelenergisch_norm_ids, ("pakt-325-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-325-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #326 CmbManifest
    # ------------------------------------------------------------------

    def test_kki_cmb_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_cmb_manifest(manifest_id="manifest-326-stability")
        norm = next(n for n in manifest.normen if n.geltung is CmbGeltung.GESPERRT)

        self.assertIsInstance(manifest, CmbManifest)
        self.assertIsInstance(norm, CmbNorm)
        self.assertEqual(norm.cmb_typ, CmbTyp.SCHUTZ_CMB)
        self.assertEqual(norm.prozedur, CmbProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.cmb_tier, 1)

    def test_kki_cmb_manifest_builds_cmbradiiert_ordnungs_norm(self) -> None:
        manifest = build_cmb_manifest(manifest_id="manifest-326-governance")
        norm = next(n for n in manifest.normen if n.geltung is CmbGeltung.CMBRADIIERT)

        self.assertEqual(norm.cmb_typ, CmbTyp.ORDNUNGS_CMB)
        self.assertEqual(norm.prozedur, CmbProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.cmb_weight, 0.0)

    def test_kki_cmb_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_cmb_manifest(manifest_id="manifest-326-expansion")
        norm = next(n for n in manifest.normen if n.geltung is CmbGeltung.GRUNDLEGEND_CMBRADIIERT)

        self.assertEqual(norm.cmb_typ, CmbTyp.SOUVERAENITAETS_CMB)
        self.assertEqual(norm.prozedur, CmbProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_cmb_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_cmb_manifest(manifest_id="manifest-326-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-326-signal-stability-lane",))
        self.assertEqual(manifest.cmbradiiert_norm_ids, ("manifest-326-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-326-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #327 StrukturbildungsSenat
    # ------------------------------------------------------------------

    def test_kki_strukturbildungs_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_strukturbildungs_senat(senat_id="senat-327-stability")
        norm = next(n for n in senat.normen if n.geltung is StrukturbildungsGeltung.GESPERRT)

        self.assertIsInstance(senat, StrukturbildungsSenat)
        self.assertIsInstance(norm, StrukturbildungsNorm)
        self.assertEqual(norm.strukturbildungs_typ, StrukturbildungsTyp.SCHUTZ_STRUKTURBILDUNG)
        self.assertEqual(norm.prozedur, StrukturbildungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.strukturbildungs_tier, 1)

    def test_kki_strukturbildungs_senat_builds_strukturbildend_ordnungs_norm(self) -> None:
        senat = build_strukturbildungs_senat(senat_id="senat-327-governance")
        norm = next(n for n in senat.normen if n.geltung is StrukturbildungsGeltung.STRUKTURBILDEND)

        self.assertEqual(norm.strukturbildungs_typ, StrukturbildungsTyp.ORDNUNGS_STRUKTURBILDUNG)
        self.assertEqual(norm.prozedur, StrukturbildungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.strukturbildungs_weight, 0.0)

    def test_kki_strukturbildungs_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_strukturbildungs_senat(senat_id="senat-327-expansion")
        norm = next(n for n in senat.normen if n.geltung is StrukturbildungsGeltung.GRUNDLEGEND_STRUKTURBILDEND)

        self.assertEqual(norm.strukturbildungs_typ, StrukturbildungsTyp.SOUVERAENITAETS_STRUKTURBILDUNG)
        self.assertEqual(norm.prozedur, StrukturbildungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_strukturbildungs_senat_aggregates_senat_signal(self) -> None:
        senat = build_strukturbildungs_senat(senat_id="senat-327-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-327-signal-stability-lane",))
        self.assertEqual(senat.strukturbildend_norm_ids, ("senat-327-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-327-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #328 ExpansionNorm  (*_norm pattern)
    # ------------------------------------------------------------------

    def test_kki_expansion_norm_builds_gesperrt_schutz_eintrag(self) -> None:
        satz = build_expansion_norm(norm_id="expansion-norm-328-stability")
        eintrag = next(n for n in satz.normen if n.geltung is ExpansionNormGeltung.GESPERRT)

        self.assertIsInstance(satz, ExpansionNormSatz)
        self.assertIsInstance(eintrag, ExpansionNormEintrag)
        self.assertEqual(eintrag.expansion_norm_typ, ExpansionNormTyp.SCHUTZ_EXPANSION)
        self.assertEqual(eintrag.prozedur, ExpansionNormProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.expansion_norm_tier, 1)

    def test_kki_expansion_norm_builds_expansionsnormiert_ordnungs_eintrag(self) -> None:
        satz = build_expansion_norm(norm_id="expansion-norm-328-governance")
        eintrag = next(n for n in satz.normen if n.geltung is ExpansionNormGeltung.EXPANSIONSNORMIERT)

        self.assertEqual(eintrag.expansion_norm_typ, ExpansionNormTyp.ORDNUNGS_EXPANSION)
        self.assertEqual(eintrag.prozedur, ExpansionNormProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.expansion_norm_weight, 0.0)

    def test_kki_expansion_norm_builds_grundlegend_souveraenitaets_eintrag(self) -> None:
        satz = build_expansion_norm(norm_id="expansion-norm-328-expansion")
        eintrag = next(n for n in satz.normen if n.geltung is ExpansionNormGeltung.GRUNDLEGEND_EXPANSIONSNORMIERT)

        self.assertEqual(eintrag.expansion_norm_typ, ExpansionNormTyp.SOUVERAENITAETS_EXPANSION)
        self.assertEqual(eintrag.prozedur, ExpansionNormProzedur.PLENARPROTOKOLL)
        self.assertTrue(eintrag.canonical)

    def test_kki_expansion_norm_aggregates_norm_signal(self) -> None:
        satz = build_expansion_norm(norm_id="expansion-norm-328-signal")

        self.assertEqual(satz.norm_signal.status, "norm-gesperrt")
        self.assertEqual(satz.gesperrt_norm_ids, ("expansion-norm-328-signal-stability-lane",))
        self.assertEqual(satz.expansionsnormiert_norm_ids, ("expansion-norm-328-signal-governance-lane",))
        self.assertEqual(satz.grundlegend_norm_ids, ("expansion-norm-328-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #329 HubbleCharta
    # ------------------------------------------------------------------

    def test_kki_hubble_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_hubble_charta(charta_id="charta-329-stability")
        norm = next(n for n in charta.normen if n.geltung is HubbleGeltung.GESPERRT)

        self.assertIsInstance(charta, HubbleCharta)
        self.assertIsInstance(norm, HubbleNorm)
        self.assertEqual(norm.hubble_typ, HubbleTyp.SCHUTZ_HUBBLE)
        self.assertEqual(norm.prozedur, HubbleProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.hubble_tier, 1)

    def test_kki_hubble_charta_builds_hubblegebunden_ordnungs_norm(self) -> None:
        charta = build_hubble_charta(charta_id="charta-329-governance")
        norm = next(n for n in charta.normen if n.geltung is HubbleGeltung.HUBBLEGEBUNDEN)

        self.assertEqual(norm.hubble_typ, HubbleTyp.ORDNUNGS_HUBBLE)
        self.assertEqual(norm.prozedur, HubbleProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.hubble_weight, 0.0)

    def test_kki_hubble_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_hubble_charta(charta_id="charta-329-expansion")
        norm = next(n for n in charta.normen if n.geltung is HubbleGeltung.GRUNDLEGEND_HUBBLEGEBUNDEN)

        self.assertEqual(norm.hubble_typ, HubbleTyp.SOUVERAENITAETS_HUBBLE)
        self.assertEqual(norm.prozedur, HubbleProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_hubble_charta_aggregates_charta_signal(self) -> None:
        charta = build_hubble_charta(charta_id="charta-329-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-329-signal-stability-lane",))
        self.assertEqual(charta.hubblegebunden_norm_ids, ("charta-329-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-329-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #330 KosmologieVerfassung  (Block-Krone)
    # ------------------------------------------------------------------

    def test_kki_kosmologie_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_kosmologie_verfassung(verfassung_id="verfassung-330-stability")
        norm = next(n for n in verfassung.normen if n.geltung is KosmologieVerfassungsGeltung.GESPERRT)

        self.assertIsInstance(verfassung, KosmologieVerfassung)
        self.assertIsInstance(norm, KosmologieVerfassungsNorm)
        self.assertEqual(norm.kosmologie_verfassungs_typ, KosmologieVerfassungsTyp.SCHUTZ_KOSMOLOGIEVERFASSUNG)
        self.assertEqual(norm.prozedur, KosmologieVerfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kosmologie_verfassungs_tier, 1)

    def test_kki_kosmologie_verfassung_builds_kosmologieverfasst_ordnungs_norm(self) -> None:
        verfassung = build_kosmologie_verfassung(verfassung_id="verfassung-330-governance")
        norm = next(n for n in verfassung.normen if n.geltung is KosmologieVerfassungsGeltung.KOSMOLOGIEVERFASST)

        self.assertEqual(norm.kosmologie_verfassungs_typ, KosmologieVerfassungsTyp.ORDNUNGS_KOSMOLOGIEVERFASSUNG)
        self.assertEqual(norm.prozedur, KosmologieVerfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kosmologie_verfassungs_weight, 0.0)

    def test_kki_kosmologie_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_kosmologie_verfassung(verfassung_id="verfassung-330-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is KosmologieVerfassungsGeltung.GRUNDLEGEND_KOSMOLOGIEVERFASST)

        self.assertEqual(norm.kosmologie_verfassungs_typ, KosmologieVerfassungsTyp.SOUVERAENITAETS_KOSMOLOGIEVERFASSUNG)
        self.assertEqual(norm.prozedur, KosmologieVerfassungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_kosmologie_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_kosmologie_verfassung(verfassung_id="verfassung-330-signal")

        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-330-signal-stability-lane",))
        self.assertEqual(verfassung.kosmologieverfasst_norm_ids, ("verfassung-330-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-330-signal-expansion-lane",))

    # #331 AstrophysikFeld

    def test_kki_astrophysik_feld_builds_gesperrt_schutz_norm(self) -> None:
        feld = build_astrophysik_feld(feld_id="feld-331-stability")
        norm = next(n for n in feld.normen if n.geltung is AstrophysikGeltung.GESPERRT)

        self.assertIsInstance(feld, AstrophysikFeld)
        self.assertIsInstance(norm, AstrophysikNorm)
        self.assertEqual(norm.astrophysik_typ, AstrophysikTyp.SCHUTZ_ASTROPHYSIK)
        self.assertEqual(norm.prozedur, AstrophysikProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.astrophysik_tier, 1)

    def test_kki_astrophysik_feld_builds_astrophysikalisch_ordnungs_norm(self) -> None:
        feld = build_astrophysik_feld(feld_id="feld-331-governance")
        norm = next(n for n in feld.normen if n.geltung is AstrophysikGeltung.ASTROPHYSIKALISCH)

        self.assertEqual(norm.astrophysik_typ, AstrophysikTyp.ORDNUNGS_ASTROPHYSIK)
        self.assertEqual(norm.prozedur, AstrophysikProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.astrophysik_weight, 0.0)

    def test_kki_astrophysik_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        feld = build_astrophysik_feld(feld_id="feld-331-expansion")
        norm = next(n for n in feld.normen if n.geltung is AstrophysikGeltung.GRUNDLEGEND_ASTROPHYSIKALISCH)

        self.assertEqual(norm.astrophysik_typ, AstrophysikTyp.SOUVERAENITAETS_ASTROPHYSIK)
        self.assertEqual(norm.prozedur, AstrophysikProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.astrophysik_weight, 0.0)

    def test_kki_astrophysik_feld_aggregates_feld_signal(self) -> None:
        feld = build_astrophysik_feld(feld_id="feld-331-signal")

        self.assertEqual(feld.feld_signal.status, "feld-gesperrt")
        self.assertEqual(feld.gesperrt_norm_ids, ("feld-331-signal-stability-lane",))
        self.assertEqual(feld.astrophysikalisch_norm_ids, ("feld-331-signal-governance-lane",))
        self.assertEqual(feld.grundlegend_norm_ids, ("feld-331-signal-expansion-lane",))

    # #332 ProtostellarRegister

    def test_kki_protostellar_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_protostellar_register(register_id="register-332-stability")
        norm = next(n for n in register.normen if n.geltung is ProtostellarGeltung.GESPERRT)

        self.assertIsInstance(register, ProtostellarRegister)
        self.assertIsInstance(norm, ProtostellarNorm)
        self.assertEqual(norm.protostellar_typ, ProtostellarTyp.SCHUTZ_PROTOSTELLAR)
        self.assertEqual(norm.prozedur, ProtostellarProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.protostellar_tier, 1)

    def test_kki_protostellar_register_builds_protostellar_ordnungs_norm(self) -> None:
        register = build_protostellar_register(register_id="register-332-governance")
        norm = next(n for n in register.normen if n.geltung is ProtostellarGeltung.PROTOSTELLAR)

        self.assertEqual(norm.protostellar_typ, ProtostellarTyp.ORDNUNGS_PROTOSTELLAR)
        self.assertEqual(norm.prozedur, ProtostellarProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.protostellar_weight, 0.0)

    def test_kki_protostellar_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_protostellar_register(register_id="register-332-expansion")
        norm = next(n for n in register.normen if n.geltung is ProtostellarGeltung.GRUNDLEGEND_PROTOSTELLAR)

        self.assertEqual(norm.protostellar_typ, ProtostellarTyp.SOUVERAENITAETS_PROTOSTELLAR)
        self.assertEqual(norm.prozedur, ProtostellarProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.protostellar_weight, 0.0)

    def test_kki_protostellar_register_aggregates_register_signal(self) -> None:
        register = build_protostellar_register(register_id="register-332-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-332-signal-stability-lane",))
        self.assertEqual(register.protostellar_norm_ids, ("register-332-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-332-signal-expansion-lane",))

    # #333 HauptreihenchartaCharta

    def test_kki_hauptreihen_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_hauptreihen_charta(charta_id="charta-333-stability")
        norm = next(n for n in charta.normen if n.geltung is HauptreihenchartaGeltung.GESPERRT)

        self.assertIsInstance(charta, HauptreihenchartaCharta)
        self.assertIsInstance(norm, HauptreihenchartaNorm)
        self.assertEqual(norm.hauptreihen_typ, HauptreihenchartaTyp.SCHUTZ_HAUPTREIHE)
        self.assertEqual(norm.prozedur, HauptreihenchartaProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.hauptreihen_tier, 1)

    def test_kki_hauptreihen_charta_builds_hauptreihenstabil_ordnungs_norm(self) -> None:
        charta = build_hauptreihen_charta(charta_id="charta-333-governance")
        norm = next(n for n in charta.normen if n.geltung is HauptreihenchartaGeltung.HAUPTREIHENSTABIL)

        self.assertEqual(norm.hauptreihen_typ, HauptreihenchartaTyp.ORDNUNGS_HAUPTREIHE)
        self.assertEqual(norm.prozedur, HauptreihenchartaProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.hauptreihen_weight, 0.0)

    def test_kki_hauptreihen_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_hauptreihen_charta(charta_id="charta-333-expansion")
        norm = next(n for n in charta.normen if n.geltung is HauptreihenchartaGeltung.GRUNDLEGEND_HAUPTREIHENSTABIL)

        self.assertEqual(norm.hauptreihen_typ, HauptreihenchartaTyp.SOUVERAENITAETS_HAUPTREIHE)
        self.assertEqual(norm.prozedur, HauptreihenchartaProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.hauptreihen_weight, 0.0)

    def test_kki_hauptreihen_charta_aggregates_charta_signal(self) -> None:
        charta = build_hauptreihen_charta(charta_id="charta-333-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-333-signal-stability-lane",))
        self.assertEqual(charta.hauptreihenstabil_norm_ids, ("charta-333-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-333-signal-expansion-lane",))

    # #334 FusionsreaktorKodex

    def test_kki_fusionsreaktor_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_fusionsreaktor_kodex(kodex_id="kodex-334-stability")
        norm = next(n for n in kodex.normen if n.geltung is FusionsreaktorGeltung.GESPERRT)

        self.assertIsInstance(kodex, FusionsreaktorKodex)
        self.assertIsInstance(norm, FusionsreaktorNorm)
        self.assertEqual(norm.fusionsreaktor_typ, FusionsreaktorTyp.SCHUTZ_FUSIONSREAKTOR)
        self.assertEqual(norm.prozedur, FusionsreaktorProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.fusionsreaktor_tier, 1)

    def test_kki_fusionsreaktor_kodex_builds_fusionsaktiv_ordnungs_norm(self) -> None:
        kodex = build_fusionsreaktor_kodex(kodex_id="kodex-334-governance")
        norm = next(n for n in kodex.normen if n.geltung is FusionsreaktorGeltung.FUSIONSAKTIV)

        self.assertEqual(norm.fusionsreaktor_typ, FusionsreaktorTyp.ORDNUNGS_FUSIONSREAKTOR)
        self.assertEqual(norm.prozedur, FusionsreaktorProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.fusionsreaktor_weight, 0.0)

    def test_kki_fusionsreaktor_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_fusionsreaktor_kodex(kodex_id="kodex-334-expansion")
        norm = next(n for n in kodex.normen if n.geltung is FusionsreaktorGeltung.GRUNDLEGEND_FUSIONSAKTIV)

        self.assertEqual(norm.fusionsreaktor_typ, FusionsreaktorTyp.SOUVERAENITAETS_FUSIONSREAKTOR)
        self.assertEqual(norm.prozedur, FusionsreaktorProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.fusionsreaktor_weight, 0.0)

    def test_kki_fusionsreaktor_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_fusionsreaktor_kodex(kodex_id="kodex-334-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-334-signal-stability-lane",))
        self.assertEqual(kodex.fusionsaktiv_norm_ids, ("kodex-334-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-334-signal-expansion-lane",))

    # #335 RoterRiesePakt

    def test_kki_roter_riese_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_roter_riese_pakt(pakt_id="pakt-335-stability")
        norm = next(n for n in pakt.normen if n.geltung is RoterRieseGeltung.GESPERRT)

        self.assertIsInstance(pakt, RoterRiesePakt)
        self.assertIsInstance(norm, RoterRieseNorm)
        self.assertEqual(norm.roter_riese_typ, RoterRieseTyp.SCHUTZ_ROTER_RIESE)
        self.assertEqual(norm.prozedur, RoterRieseProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.roter_riese_tier, 1)

    def test_kki_roter_riese_pakt_builds_riesenphasig_ordnungs_norm(self) -> None:
        pakt = build_roter_riese_pakt(pakt_id="pakt-335-governance")
        norm = next(n for n in pakt.normen if n.geltung is RoterRieseGeltung.RIESENPHASIG)

        self.assertEqual(norm.roter_riese_typ, RoterRieseTyp.ORDNUNGS_ROTER_RIESE)
        self.assertEqual(norm.prozedur, RoterRieseProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.roter_riese_weight, 0.0)

    def test_kki_roter_riese_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_roter_riese_pakt(pakt_id="pakt-335-expansion")
        norm = next(n for n in pakt.normen if n.geltung is RoterRieseGeltung.GRUNDLEGEND_RIESENPHASIG)

        self.assertEqual(norm.roter_riese_typ, RoterRieseTyp.SOUVERAENITAETS_ROTER_RIESE)
        self.assertEqual(norm.prozedur, RoterRieseProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.roter_riese_weight, 0.0)

    def test_kki_roter_riese_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_roter_riese_pakt(pakt_id="pakt-335-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-335-signal-stability-lane",))
        self.assertEqual(pakt.riesenphasig_norm_ids, ("pakt-335-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-335-signal-expansion-lane",))

    # #336 SupernovaManifest

    def test_kki_supernova_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_supernova_manifest(manifest_id="manifest-336-stability")
        norm = next(n for n in manifest.normen if n.geltung is SupernovaGeltung.GESPERRT)

        self.assertIsInstance(manifest, SupernovaManifest)
        self.assertIsInstance(norm, SupernovaNorm)
        self.assertEqual(norm.supernova_typ, SupernovaTyp.SCHUTZ_SUPERNOVA)
        self.assertEqual(norm.prozedur, SupernovaProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.supernova_tier, 1)

    def test_kki_supernova_manifest_builds_supernovaexplosiv_ordnungs_norm(self) -> None:
        manifest = build_supernova_manifest(manifest_id="manifest-336-governance")
        norm = next(n for n in manifest.normen if n.geltung is SupernovaGeltung.SUPERNOVAEXPLOSIV)

        self.assertEqual(norm.supernova_typ, SupernovaTyp.ORDNUNGS_SUPERNOVA)
        self.assertEqual(norm.prozedur, SupernovaProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.supernova_weight, 0.0)

    def test_kki_supernova_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_supernova_manifest(manifest_id="manifest-336-expansion")
        norm = next(n for n in manifest.normen if n.geltung is SupernovaGeltung.GRUNDLEGEND_SUPERNOVAEXPLOSIV)

        self.assertEqual(norm.supernova_typ, SupernovaTyp.SOUVERAENITAETS_SUPERNOVA)
        self.assertEqual(norm.prozedur, SupernovaProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.supernova_weight, 0.0)

    def test_kki_supernova_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_supernova_manifest(manifest_id="manifest-336-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-336-signal-stability-lane",))
        self.assertEqual(manifest.supernovaexplosiv_norm_ids, ("manifest-336-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-336-signal-expansion-lane",))

    # #337 NeutronensternSenat

    def test_kki_neutronenstern_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_neutronenstern_senat(senat_id="senat-337-stability")
        norm = next(n for n in senat.normen if n.geltung is NeutronensternGeltung.GESPERRT)

        self.assertIsInstance(senat, NeutronensternSenat)
        self.assertIsInstance(norm, NeutronensternNorm)
        self.assertEqual(norm.neutronenstern_typ, NeutronensternTyp.SCHUTZ_NEUTRONENSTERN)
        self.assertEqual(norm.prozedur, NeutronensternProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.neutronenstern_tier, 1)

    def test_kki_neutronenstern_senat_builds_neutronendicht_ordnungs_norm(self) -> None:
        senat = build_neutronenstern_senat(senat_id="senat-337-governance")
        norm = next(n for n in senat.normen if n.geltung is NeutronensternGeltung.NEUTRONENDICHT)

        self.assertEqual(norm.neutronenstern_typ, NeutronensternTyp.ORDNUNGS_NEUTRONENSTERN)
        self.assertEqual(norm.prozedur, NeutronensternProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.neutronenstern_weight, 0.0)

    def test_kki_neutronenstern_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_neutronenstern_senat(senat_id="senat-337-expansion")
        norm = next(n for n in senat.normen if n.geltung is NeutronensternGeltung.GRUNDLEGEND_NEUTRONENDICHT)

        self.assertEqual(norm.neutronenstern_typ, NeutronensternTyp.SOUVERAENITAETS_NEUTRONENSTERN)
        self.assertEqual(norm.prozedur, NeutronensternProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.neutronenstern_weight, 0.0)

    def test_kki_neutronenstern_senat_aggregates_senat_signal(self) -> None:
        senat = build_neutronenstern_senat(senat_id="senat-337-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-337-signal-stability-lane",))
        self.assertEqual(senat.neutronendicht_norm_ids, ("senat-337-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-337-signal-expansion-lane",))

    # #338 SchwarzerLochNormSatz (*_norm)

    def test_kki_schwarzes_loch_norm_builds_gesperrt_schutz_norm(self) -> None:
        normsatz = build_schwarzes_loch_norm(norm_id="schwarzes-loch-338-stability")
        eintrag = next(n for n in normsatz.normen if n.geltung is SchwarzerLochNormGeltung.GESPERRT)

        self.assertIsInstance(normsatz, SchwarzerLochNormSatz)
        self.assertIsInstance(eintrag, SchwarzerLochNormEintrag)
        self.assertEqual(eintrag.schwarzes_loch_norm_typ, SchwarzerLochNormTyp.SCHUTZ_SCHWARZES_LOCH)
        self.assertEqual(eintrag.prozedur, SchwarzerLochNormProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.schwarzes_loch_norm_tier, 1)

    def test_kki_schwarzes_loch_norm_builds_horizontgebunden_ordnungs_norm(self) -> None:
        normsatz = build_schwarzes_loch_norm(norm_id="schwarzes-loch-338-governance")
        eintrag = next(n for n in normsatz.normen if n.geltung is SchwarzerLochNormGeltung.HORIZONTGEBUNDEN)

        self.assertEqual(eintrag.schwarzes_loch_norm_typ, SchwarzerLochNormTyp.ORDNUNGS_SCHWARZES_LOCH)
        self.assertEqual(eintrag.prozedur, SchwarzerLochNormProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.schwarzes_loch_norm_weight, 0.0)

    def test_kki_schwarzes_loch_norm_builds_grundlegend_souveraenitaets_norm(self) -> None:
        normsatz = build_schwarzes_loch_norm(norm_id="schwarzes-loch-338-expansion")
        eintrag = next(n for n in normsatz.normen if n.geltung is SchwarzerLochNormGeltung.GRUNDLEGEND_HORIZONTGEBUNDEN)

        self.assertEqual(eintrag.schwarzes_loch_norm_typ, SchwarzerLochNormTyp.SOUVERAENITAETS_SCHWARZES_LOCH)
        self.assertEqual(eintrag.prozedur, SchwarzerLochNormProzedur.PLENARPROTOKOLL)
        self.assertGreater(eintrag.schwarzes_loch_norm_weight, 0.0)

    def test_kki_schwarzes_loch_norm_aggregates_norm_signal(self) -> None:
        normsatz = build_schwarzes_loch_norm(norm_id="schwarzes-loch-338-signal")

        self.assertEqual(normsatz.norm_signal.status, "norm-gesperrt")
        self.assertEqual(normsatz.gesperrt_norm_ids, ("schwarzes-loch-338-signal-stability-lane",))
        self.assertEqual(normsatz.horizontgebunden_norm_ids, ("schwarzes-loch-338-signal-governance-lane",))
        self.assertEqual(normsatz.grundlegend_norm_ids, ("schwarzes-loch-338-signal-expansion-lane",))

    # #339 HertzsprungRussellCharta

    def test_kki_hertzsprung_russell_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_hertzsprung_russell_charta(charta_id="charta-339-stability")
        norm = next(n for n in charta.normen if n.geltung is HertzsprungRussellGeltung.GESPERRT)

        self.assertIsInstance(charta, HertzsprungRussellCharta)
        self.assertIsInstance(norm, HertzsprungRussellNorm)
        self.assertEqual(norm.hertzsprung_russell_typ, HertzsprungRussellTyp.SCHUTZ_HERTZSPRUNG_RUSSELL)
        self.assertEqual(norm.prozedur, HertzsprungRussellProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.hertzsprung_russell_tier, 1)

    def test_kki_hertzsprung_russell_charta_builds_hrdiagrammiert_ordnungs_norm(self) -> None:
        charta = build_hertzsprung_russell_charta(charta_id="charta-339-governance")
        norm = next(n for n in charta.normen if n.geltung is HertzsprungRussellGeltung.HRDIAGRAMMIERT)

        self.assertEqual(norm.hertzsprung_russell_typ, HertzsprungRussellTyp.ORDNUNGS_HERTZSPRUNG_RUSSELL)
        self.assertEqual(norm.prozedur, HertzsprungRussellProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.hertzsprung_russell_weight, 0.0)

    def test_kki_hertzsprung_russell_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_hertzsprung_russell_charta(charta_id="charta-339-expansion")
        norm = next(n for n in charta.normen if n.geltung is HertzsprungRussellGeltung.GRUNDLEGEND_HRDIAGRAMMIERT)

        self.assertEqual(norm.hertzsprung_russell_typ, HertzsprungRussellTyp.SOUVERAENITAETS_HERTZSPRUNG_RUSSELL)
        self.assertEqual(norm.prozedur, HertzsprungRussellProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.hertzsprung_russell_weight, 0.0)

    def test_kki_hertzsprung_russell_charta_aggregates_charta_signal(self) -> None:
        charta = build_hertzsprung_russell_charta(charta_id="charta-339-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-339-signal-stability-lane",))
        self.assertEqual(charta.hrdiagrammiert_norm_ids, ("charta-339-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-339-signal-expansion-lane",))

    # #340 AstrophysikVerfassung (Block-Krone)

    def test_kki_astrophysik_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_astrophysik_verfassung(verfassung_id="verfassung-340-stability")
        norm = next(n for n in verfassung.normen if n.geltung is AstrophysikVerfassungsGeltung.GESPERRT)

        self.assertIsInstance(verfassung, AstrophysikVerfassung)
        self.assertIsInstance(norm, AstrophysikVerfassungsNorm)
        self.assertEqual(norm.astrophysik_verfassungs_typ, AstrophysikVerfassungsTyp.SCHUTZ_ASTROPHYSIKVERFASSUNG)
        self.assertEqual(norm.prozedur, AstrophysikVerfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.astrophysik_verfassungs_tier, 1)

    def test_kki_astrophysik_verfassung_builds_astrophysikverfasst_ordnungs_norm(self) -> None:
        verfassung = build_astrophysik_verfassung(verfassung_id="verfassung-340-governance")
        norm = next(n for n in verfassung.normen if n.geltung is AstrophysikVerfassungsGeltung.ASTROPHYSIKVERFASST)

        self.assertEqual(norm.astrophysik_verfassungs_typ, AstrophysikVerfassungsTyp.ORDNUNGS_ASTROPHYSIKVERFASSUNG)
        self.assertEqual(norm.prozedur, AstrophysikVerfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.astrophysik_verfassungs_weight, 0.0)

    def test_kki_astrophysik_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_astrophysik_verfassung(verfassung_id="verfassung-340-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is AstrophysikVerfassungsGeltung.GRUNDLEGEND_ASTROPHYSIKVERFASST)

        self.assertEqual(norm.astrophysik_verfassungs_typ, AstrophysikVerfassungsTyp.SOUVERAENITAETS_ASTROPHYSIKVERFASSUNG)
        self.assertEqual(norm.prozedur, AstrophysikVerfassungsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.astrophysik_verfassungs_weight, 0.0)

    def test_kki_astrophysik_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_astrophysik_verfassung(verfassung_id="verfassung-340-signal")

        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-340-signal-stability-lane",))
        self.assertEqual(verfassung.astrophysikverfasst_norm_ids, ("verfassung-340-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-340-signal-expansion-lane",))

    def test_kki_waermestrahlung_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_waermestrahlung_charta(charta_id="charta-289-stability")
        norm = next(n for n in charta.normen if n.geltung is WaermestrahlungsGeltung.GESPERRT)

        self.assertIsInstance(charta, WaermestrahlungsCharta)
        self.assertIsInstance(norm, WaermestrahlungsNorm)
        self.assertEqual(norm.waermestrahlung_typ, WaermestrahlungsTyp.SCHUTZ_WAERMESTRAHLUNG)
        self.assertEqual(norm.prozedur, WaermestrahlungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.waermestrahlung_tier, 1)

    def test_kki_waermestrahlung_charta_builds_strahlend_ordnungs_norm(self) -> None:
        charta = build_waermestrahlung_charta(charta_id="charta-289-governance")
        norm = next(n for n in charta.normen if n.geltung is WaermestrahlungsGeltung.STRAHLEND)

        self.assertEqual(norm.waermestrahlung_typ, WaermestrahlungsTyp.ORDNUNGS_WAERMESTRAHLUNG)
        self.assertEqual(norm.prozedur, WaermestrahlungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.waermestrahlung_weight, 0.0)

    def test_kki_waermestrahlung_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_waermestrahlung_charta(charta_id="charta-289-expansion")
        norm = next(n for n in charta.normen if n.geltung is WaermestrahlungsGeltung.GRUNDLEGEND_STRAHLEND)

        self.assertEqual(norm.waermestrahlung_typ, WaermestrahlungsTyp.SOUVERAENITAETS_WAERMESTRAHLUNG)
        self.assertEqual(norm.prozedur, WaermestrahlungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_waermestrahlung_charta_aggregates_charta_signal(self) -> None:
        charta = build_waermestrahlung_charta(charta_id="charta-289-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-289-signal-stability-lane",))
        self.assertEqual(charta.strahlend_norm_ids, ("charta-289-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-289-signal-expansion-lane",))

    def test_kki_entropie_norm_builds_gesperrt_schutz_eintrag(self) -> None:
        satz = build_entropie_norm(norm_id="norm-288-stability")
        eintrag = next(n for n in satz.normen if n.geltung is EntropieNormGeltung.GESPERRT)

        self.assertIsInstance(satz, EntropieNormSatz)
        self.assertIsInstance(eintrag, EntropieNormEintrag)
        self.assertEqual(eintrag.entropie_norm_typ, EntropieNormTyp.SCHUTZ_ENTROPIENORM)
        self.assertEqual(eintrag.prozedur, EntropieNormProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.entropie_norm_tier, 1)

    def test_kki_entropie_norm_builds_entropienormiert_ordnungs_eintrag(self) -> None:
        satz = build_entropie_norm(norm_id="norm-288-governance")
        eintrag = next(n for n in satz.normen if n.geltung is EntropieNormGeltung.ENTROPIENORMIERT)

        self.assertEqual(eintrag.entropie_norm_typ, EntropieNormTyp.ORDNUNGS_ENTROPIENORM)
        self.assertEqual(eintrag.prozedur, EntropieNormProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.entropie_norm_weight, 0.0)

    def test_kki_entropie_norm_builds_grundlegend_souveraenitaets_eintrag(self) -> None:
        satz = build_entropie_norm(norm_id="norm-288-expansion")
        eintrag = next(n for n in satz.normen if n.geltung is EntropieNormGeltung.GRUNDLEGEND_ENTROPIENORMIERT)

        self.assertEqual(eintrag.entropie_norm_typ, EntropieNormTyp.SOUVERAENITAETS_ENTROPIENORM)
        self.assertEqual(eintrag.prozedur, EntropieNormProzedur.PLENARPROTOKOLL)
        self.assertTrue(eintrag.canonical)

    def test_kki_entropie_norm_aggregates_norm_signal(self) -> None:
        satz = build_entropie_norm(norm_id="norm-288-signal")

        self.assertEqual(satz.norm_signal.status, "norm-gesperrt")
        self.assertEqual(satz.gesperrt_norm_ids, ("norm-288-signal-stability-lane",))
        self.assertEqual(satz.entropienormiert_norm_ids, ("norm-288-signal-governance-lane",))
        self.assertEqual(satz.grundlegend_norm_ids, ("norm-288-signal-expansion-lane",))

    def test_kki_boltzmann_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_boltzmann_senat(senat_id="senat-287-stability")
        norm = next(n for n in senat.normen if n.geltung is BoltzmannGeltung.GESPERRT)

        self.assertIsInstance(senat, BoltzmannSenat)
        self.assertIsInstance(norm, BoltzmannNorm)
        self.assertEqual(norm.boltzmann_typ, BoltzmannTyp.SCHUTZ_BOLTZMANN)
        self.assertEqual(norm.prozedur, BoltzmannProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.boltzmann_tier, 1)

    def test_kki_boltzmann_senat_builds_statistisch_ordnungs_norm(self) -> None:
        senat = build_boltzmann_senat(senat_id="senat-287-governance")
        norm = next(n for n in senat.normen if n.geltung is BoltzmannGeltung.STATISTISCH)

        self.assertEqual(norm.boltzmann_typ, BoltzmannTyp.ORDNUNGS_BOLTZMANN)
        self.assertEqual(norm.prozedur, BoltzmannProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.boltzmann_weight, 0.0)

    def test_kki_boltzmann_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_boltzmann_senat(senat_id="senat-287-expansion")
        norm = next(n for n in senat.normen if n.geltung is BoltzmannGeltung.GRUNDLEGEND_STATISTISCH)

        self.assertEqual(norm.boltzmann_typ, BoltzmannTyp.SOUVERAENITAETS_BOLTZMANN)
        self.assertEqual(norm.prozedur, BoltzmannProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_boltzmann_senat_aggregates_senat_signal(self) -> None:
        senat = build_boltzmann_senat(senat_id="senat-287-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-287-signal-stability-lane",))
        self.assertEqual(senat.statistisch_norm_ids, ("senat-287-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-287-signal-expansion-lane",))

    def test_kki_carnot_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_carnot_manifest(manifest_id="manifest-286-stability")
        norm = next(n for n in manifest.normen if n.geltung is CarnotGeltung.GESPERRT)

        self.assertIsInstance(manifest, CarnotManifest)
        self.assertIsInstance(norm, CarnotNorm)
        self.assertEqual(norm.carnot_typ, CarnotTyp.SCHUTZ_CARNOT)
        self.assertEqual(norm.prozedur, CarnotProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.carnot_tier, 1)

    def test_kki_carnot_manifest_builds_carnotisch_ordnungs_norm(self) -> None:
        manifest = build_carnot_manifest(manifest_id="manifest-286-governance")
        norm = next(n for n in manifest.normen if n.geltung is CarnotGeltung.CARNOTISCH)

        self.assertEqual(norm.carnot_typ, CarnotTyp.ORDNUNGS_CARNOT)
        self.assertEqual(norm.prozedur, CarnotProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.carnot_weight, 0.0)

    def test_kki_carnot_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_carnot_manifest(manifest_id="manifest-286-expansion")
        norm = next(n for n in manifest.normen if n.geltung is CarnotGeltung.GRUNDLEGEND_CARNOTISCH)

        self.assertEqual(norm.carnot_typ, CarnotTyp.SOUVERAENITAETS_CARNOT)
        self.assertEqual(norm.prozedur, CarnotProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_carnot_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_carnot_manifest(manifest_id="manifest-286-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-286-signal-stability-lane",))
        self.assertEqual(manifest.carnotisch_norm_ids, ("manifest-286-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-286-signal-expansion-lane",))

    def test_kki_gleichgewichts_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_gleichgewichts_pakt(pakt_id="pakt-285-stability")
        norm = next(n for n in pakt.normen if n.geltung is GleichgewichtsGeltung.GESPERRT)

        self.assertIsInstance(pakt, GleichgewichtsPakt)
        self.assertIsInstance(norm, GleichgewichtsNorm)
        self.assertEqual(norm.gleichgewichts_typ, GleichgewichtsTyp.SCHUTZ_GLEICHGEWICHT)
        self.assertEqual(norm.prozedur, GleichgewichtsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.gleichgewichts_tier, 1)

    def test_kki_gleichgewichts_pakt_builds_equilibriert_ordnungs_norm(self) -> None:
        pakt = build_gleichgewichts_pakt(pakt_id="pakt-285-governance")
        norm = next(n for n in pakt.normen if n.geltung is GleichgewichtsGeltung.EQUILIBRIERT)

        self.assertEqual(norm.gleichgewichts_typ, GleichgewichtsTyp.ORDNUNGS_GLEICHGEWICHT)
        self.assertEqual(norm.prozedur, GleichgewichtsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.gleichgewichts_weight, 0.0)

    def test_kki_gleichgewichts_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_gleichgewichts_pakt(pakt_id="pakt-285-expansion")
        norm = next(n for n in pakt.normen if n.geltung is GleichgewichtsGeltung.GRUNDLEGEND_EQUILIBRIERT)

        self.assertEqual(norm.gleichgewichts_typ, GleichgewichtsTyp.SOUVERAENITAETS_GLEICHGEWICHT)
        self.assertEqual(norm.prozedur, GleichgewichtsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_gleichgewichts_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_gleichgewichts_pakt(pakt_id="pakt-285-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-285-signal-stability-lane",))
        self.assertEqual(pakt.equilibriert_norm_ids, ("pakt-285-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-285-signal-expansion-lane",))

    def test_kki_energieerhaltungs_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_energieerhaltungs_kodex(kodex_id="kodex-284-stability")
        norm = next(n for n in kodex.normen if n.geltung is EnergieerhaltungsGeltung.GESPERRT)

        self.assertIsInstance(kodex, EnergieerhaltungsKodex)
        self.assertIsInstance(norm, EnergieerhaltungsNorm)
        self.assertEqual(norm.energieerhaltungs_typ, EnergieerhaltungsTyp.SCHUTZ_ENERGIEERHALTUNG)
        self.assertEqual(norm.prozedur, EnergieerhaltungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.energieerhaltungs_tier, 1)

    def test_kki_energieerhaltungs_kodex_builds_energieerhaltend_ordnungs_norm(self) -> None:
        kodex = build_energieerhaltungs_kodex(kodex_id="kodex-284-governance")
        norm = next(n for n in kodex.normen if n.geltung is EnergieerhaltungsGeltung.ENERGIEERHALTEND)

        self.assertEqual(norm.energieerhaltungs_typ, EnergieerhaltungsTyp.ORDNUNGS_ENERGIEERHALTUNG)
        self.assertEqual(norm.prozedur, EnergieerhaltungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.energieerhaltungs_weight, 0.0)

    def test_kki_energieerhaltungs_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_energieerhaltungs_kodex(kodex_id="kodex-284-expansion")
        norm = next(n for n in kodex.normen if n.geltung is EnergieerhaltungsGeltung.GRUNDLEGEND_ENERGIEERHALTEND)

        self.assertEqual(norm.energieerhaltungs_typ, EnergieerhaltungsTyp.SOUVERAENITAETS_ENERGIEERHALTUNG)
        self.assertEqual(norm.prozedur, EnergieerhaltungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_energieerhaltungs_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_energieerhaltungs_kodex(kodex_id="kodex-284-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-284-signal-stability-lane",))
        self.assertEqual(kodex.energieerhaltend_norm_ids, ("kodex-284-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-284-signal-expansion-lane",))

    def test_kki_waerme_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_waerme_charta(charta_id="charta-283-stability")
        norm = next(n for n in charta.normen if n.geltung is WaermeGeltung.GESPERRT)

        self.assertIsInstance(charta, WaermeCharta)
        self.assertIsInstance(norm, WaermeNorm)
        self.assertEqual(norm.waerme_typ, WaermeTyp.SCHUTZ_WAERME)
        self.assertEqual(norm.prozedur, WaermeProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.waerme_tier, 1)

    def test_kki_waerme_charta_builds_waermeuebertragen_ordnungs_norm(self) -> None:
        charta = build_waerme_charta(charta_id="charta-283-governance")
        norm = next(n for n in charta.normen if n.geltung is WaermeGeltung.WAERMEUEBERTRAGEN)

        self.assertEqual(norm.waerme_typ, WaermeTyp.ORDNUNGS_WAERME)
        self.assertEqual(norm.prozedur, WaermeProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.waerme_weight, 0.0)

    def test_kki_waerme_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_waerme_charta(charta_id="charta-283-expansion")
        norm = next(n for n in charta.normen if n.geltung is WaermeGeltung.GRUNDLEGEND_WAERMEUEBERTRAGEN)

        self.assertEqual(norm.waerme_typ, WaermeTyp.SOUVERAENITAETS_WAERME)
        self.assertEqual(norm.prozedur, WaermeProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_waerme_charta_aggregates_charta_signal(self) -> None:
        charta = build_waerme_charta(charta_id="charta-283-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-283-signal-stability-lane",))
        self.assertEqual(charta.waermeuebertragen_norm_ids, ("charta-283-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-283-signal-expansion-lane",))

    def test_kki_entropie_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_entropie_register(register_id="register-282-stability")
        norm = next(n for n in register.normen if n.geltung is EntropieGeltung.GESPERRT)

        self.assertIsInstance(register, EntropieRegister)
        self.assertIsInstance(norm, EntropieNorm)
        self.assertEqual(norm.entropie_typ, EntropieTyp.SCHUTZ_ENTROPIE)
        self.assertEqual(norm.prozedur, EntropieProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.entropie_tier, 1)

    def test_kki_entropie_register_builds_entropisch_ordnungs_norm(self) -> None:
        register = build_entropie_register(register_id="register-282-governance")
        norm = next(n for n in register.normen if n.geltung is EntropieGeltung.ENTROPISCH)

        self.assertEqual(norm.entropie_typ, EntropieTyp.ORDNUNGS_ENTROPIE)
        self.assertEqual(norm.prozedur, EntropieProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.entropie_weight, 0.0)

    def test_kki_entropie_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_entropie_register(register_id="register-282-expansion")
        norm = next(n for n in register.normen if n.geltung is EntropieGeltung.GRUNDLEGEND_ENTROPISCH)

        self.assertEqual(norm.entropie_typ, EntropieTyp.SOUVERAENITAETS_ENTROPIE)
        self.assertEqual(norm.prozedur, EntropieProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_entropie_register_aggregates_register_signal(self) -> None:
        register = build_entropie_register(register_id="register-282-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-282-signal-stability-lane",))
        self.assertEqual(register.entropisch_norm_ids, ("register-282-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-282-signal-expansion-lane",))

    def test_kki_thermodynamik_feld_builds_gesperrt_schutz_norm(self) -> None:
        feld = build_thermodynamik_feld(feld_id="feld-281-stability")
        norm = next(n for n in feld.normen if n.geltung is ThermodynamikGeltung.GESPERRT)

        self.assertIsInstance(feld, ThermodynamikFeld)
        self.assertIsInstance(norm, ThermodynamikNorm)
        self.assertEqual(norm.thermodynamik_typ, ThermodynamikTyp.SCHUTZ_THERMODYNAMIK)
        self.assertEqual(norm.prozedur, ThermodynamikProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.thermodynamik_tier, 1)

    def test_kki_thermodynamik_feld_builds_thermisch_ordnungs_norm(self) -> None:
        feld = build_thermodynamik_feld(feld_id="feld-281-governance")
        norm = next(n for n in feld.normen if n.geltung is ThermodynamikGeltung.THERMISCH)

        self.assertEqual(norm.thermodynamik_typ, ThermodynamikTyp.ORDNUNGS_THERMODYNAMIK)
        self.assertEqual(norm.prozedur, ThermodynamikProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.thermodynamik_weight, 0.0)

    def test_kki_thermodynamik_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        feld = build_thermodynamik_feld(feld_id="feld-281-expansion")
        norm = next(n for n in feld.normen if n.geltung is ThermodynamikGeltung.GRUNDLEGEND_THERMISCH)

        self.assertEqual(norm.thermodynamik_typ, ThermodynamikTyp.SOUVERAENITAETS_THERMODYNAMIK)
        self.assertEqual(norm.prozedur, ThermodynamikProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_thermodynamik_feld_aggregates_feld_signal(self) -> None:
        feld = build_thermodynamik_feld(feld_id="feld-281-signal")

        self.assertEqual(feld.feld_signal.status, "feld-gesperrt")
        self.assertEqual(feld.gesperrt_norm_ids, ("feld-281-signal-stability-lane",))
        self.assertEqual(feld.thermisch_norm_ids, ("feld-281-signal-governance-lane",))
        self.assertEqual(feld.grundlegend_norm_ids, ("feld-281-signal-expansion-lane",))

    def test_kki_relativitaets_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_relativitaets_verfassung(verfassung_id="verfassung-280-stability")
        norm = next(n for n in verfassung.normen if n.geltung is RelativitaetsGeltung.GESPERRT)

        self.assertIsInstance(verfassung, RelativitaetsVerfassung)
        self.assertIsInstance(norm, RelativitaetsNorm)
        self.assertEqual(norm.relativitaets_typ, RelativitaetsTyp.SCHUTZ_RELATIVITAET)
        self.assertEqual(norm.prozedur, RelativitaetsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.relativitaets_tier, 1)

    def test_kki_relativitaets_verfassung_builds_relativverfasst_ordnungs_norm(self) -> None:
        verfassung = build_relativitaets_verfassung(verfassung_id="verfassung-280-governance")
        norm = next(n for n in verfassung.normen if n.geltung is RelativitaetsGeltung.RELATIVVERFASST)

        self.assertEqual(norm.relativitaets_typ, RelativitaetsTyp.ORDNUNGS_RELATIVITAET)
        self.assertEqual(norm.prozedur, RelativitaetsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.relativitaets_weight, 0.0)

    def test_kki_relativitaets_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_relativitaets_verfassung(verfassung_id="verfassung-280-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is RelativitaetsGeltung.GRUNDLEGEND_RELATIVVERFASST)

        self.assertEqual(norm.relativitaets_typ, RelativitaetsTyp.SOUVERAENITAETS_RELATIVITAET)
        self.assertEqual(norm.prozedur, RelativitaetsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_relativitaets_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_relativitaets_verfassung(verfassung_id="verfassung-280-signal")

        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-280-signal-stability-lane",))
        self.assertEqual(verfassung.relativverfasst_norm_ids, ("verfassung-280-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-280-signal-expansion-lane",))

    def test_kki_zeitdilatations_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_zeitdilatations_charta(charta_id="charta-279-stability")
        norm = next(n for n in charta.normen if n.geltung is ZeitdilatationsGeltung.GESPERRT)

        self.assertIsInstance(charta, ZeitdilatationsCharta)
        self.assertIsInstance(norm, ZeitdilatationsNorm)
        self.assertEqual(norm.zeitdilatations_typ, ZeitdilatationsTyp.SCHUTZ_ZEITDILATATION)
        self.assertEqual(norm.prozedur, ZeitdilatationsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.zeitdilatations_tier, 1)

    def test_kki_zeitdilatations_charta_builds_zeitdilatatiert_ordnungs_norm(self) -> None:
        charta = build_zeitdilatations_charta(charta_id="charta-279-governance")
        norm = next(n for n in charta.normen if n.geltung is ZeitdilatationsGeltung.ZEITDILATATIERT)

        self.assertEqual(norm.zeitdilatations_typ, ZeitdilatationsTyp.ORDNUNGS_ZEITDILATATION)
        self.assertEqual(norm.prozedur, ZeitdilatationsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.zeitdilatations_weight, 0.0)

    def test_kki_zeitdilatations_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_zeitdilatations_charta(charta_id="charta-279-expansion")
        norm = next(n for n in charta.normen if n.geltung is ZeitdilatationsGeltung.GRUNDLEGEND_ZEITDILATATIERT)

        self.assertEqual(norm.zeitdilatations_typ, ZeitdilatationsTyp.SOUVERAENITAETS_ZEITDILATATION)
        self.assertEqual(norm.prozedur, ZeitdilatationsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_zeitdilatations_charta_aggregates_charta_signal(self) -> None:
        charta = build_zeitdilatations_charta(charta_id="charta-279-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-279-signal-stability-lane",))
        self.assertEqual(charta.zeitdilatatiert_norm_ids, ("charta-279-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-279-signal-expansion-lane",))

    def test_kki_kruemmungs_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_kruemmungs_pakt(pakt_id="pakt-275-stability")
        norm = next(n for n in pakt.normen if n.geltung is KruemmungsGeltung.GESPERRT)

        self.assertIsInstance(pakt, KruemmungsPakt)
        self.assertIsInstance(norm, KruemmungsNorm)
        self.assertEqual(norm.kruemmungs_typ, KruemmungsTyp.SCHUTZ_KRUEMMUNG)
        self.assertEqual(norm.prozedur, KruemmungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kruemmungs_tier, 1)

    def test_kki_kruemmungs_pakt_builds_gekruemmt_ordnungs_norm(self) -> None:
        pakt = build_kruemmungs_pakt(pakt_id="pakt-275-governance")
        norm = next(n for n in pakt.normen if n.geltung is KruemmungsGeltung.GEKRUEMMT)

        self.assertEqual(norm.kruemmungs_typ, KruemmungsTyp.ORDNUNGS_KRUEMMUNG)
        self.assertEqual(norm.prozedur, KruemmungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kruemmungs_weight, 0.0)

    def test_kki_kruemmungs_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_kruemmungs_pakt(pakt_id="pakt-275-expansion")
        norm = next(n for n in pakt.normen if n.geltung is KruemmungsGeltung.GRUNDLEGEND_GEKRUEMMT)

        self.assertEqual(norm.kruemmungs_typ, KruemmungsTyp.SOUVERAENITAETS_KRUEMMUNG)
        self.assertEqual(norm.prozedur, KruemmungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_kruemmungs_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_kruemmungs_pakt(pakt_id="pakt-275-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-275-signal-stability-lane",))
        self.assertEqual(pakt.gekruemmt_norm_ids, ("pakt-275-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-275-signal-expansion-lane",))

    def test_kki_gravitations_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_gravitations_kodex(kodex_id="kodex-274-stability")
        norm = next(n for n in kodex.normen if n.geltung is GravitationsGeltung.GESPERRT)

        self.assertIsInstance(kodex, GravitationsKodex)
        self.assertIsInstance(norm, GravitationsNorm)
        self.assertEqual(norm.gravitations_typ, GravitationsTyp.SCHUTZ_GRAVITATION)
        self.assertEqual(norm.prozedur, GravitationsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.gravitations_tier, 1)

    def test_kki_gravitations_kodex_builds_gravitiert_ordnungs_norm(self) -> None:
        kodex = build_gravitations_kodex(kodex_id="kodex-274-governance")
        norm = next(n for n in kodex.normen if n.geltung is GravitationsGeltung.GRAVITIERT)

        self.assertEqual(norm.gravitations_typ, GravitationsTyp.ORDNUNGS_GRAVITATION)
        self.assertEqual(norm.prozedur, GravitationsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.gravitations_weight, 0.0)

    def test_kki_gravitations_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_gravitations_kodex(kodex_id="kodex-274-expansion")
        norm = next(n for n in kodex.normen if n.geltung is GravitationsGeltung.GRUNDLEGEND_GRAVITIERT)

        self.assertEqual(norm.gravitations_typ, GravitationsTyp.SOUVERAENITAETS_GRAVITATION)
        self.assertEqual(norm.prozedur, GravitationsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_gravitations_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_gravitations_kodex(kodex_id="kodex-274-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-274-signal-stability-lane",))
        self.assertEqual(kodex.gravitiert_norm_ids, ("kodex-274-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-274-signal-expansion-lane",))

    def test_kki_lichtgeschwindigkeits_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_lichtgeschwindigkeits_charta(charta_id="charta-273-stability")
        norm = next(n for n in charta.normen if n.geltung is LichtgeschwindigkeitsGeltung.GESPERRT)

        self.assertIsInstance(charta, LichtgeschwindigkeitsCharta)
        self.assertIsInstance(norm, LichtgeschwindigkeitsNorm)
        self.assertEqual(norm.lichtgeschwindigkeits_typ, LichtgeschwindigkeitsTyp.SCHUTZ_LICHT)
        self.assertEqual(norm.prozedur, LichtgeschwindigkeitsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.lichtgeschwindigkeits_tier, 1)

    def test_kki_lichtgeschwindigkeits_charta_builds_lichtschnell_ordnungs_norm(self) -> None:
        charta = build_lichtgeschwindigkeits_charta(charta_id="charta-273-governance")
        norm = next(n for n in charta.normen if n.geltung is LichtgeschwindigkeitsGeltung.LICHTSCHNELL)

        self.assertEqual(norm.lichtgeschwindigkeits_typ, LichtgeschwindigkeitsTyp.ORDNUNGS_LICHT)
        self.assertEqual(norm.prozedur, LichtgeschwindigkeitsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.lichtgeschwindigkeits_weight, 0.0)

    def test_kki_lichtgeschwindigkeits_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_lichtgeschwindigkeits_charta(charta_id="charta-273-expansion")
        norm = next(n for n in charta.normen if n.geltung is LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL)

        self.assertEqual(norm.lichtgeschwindigkeits_typ, LichtgeschwindigkeitsTyp.SOUVERAENITAETS_LICHT)
        self.assertEqual(norm.prozedur, LichtgeschwindigkeitsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_lichtgeschwindigkeits_charta_aggregates_charta_signal(self) -> None:
        charta = build_lichtgeschwindigkeits_charta(charta_id="charta-273-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-273-signal-stability-lane",))
        self.assertEqual(charta.lichtschnell_norm_ids, ("charta-273-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-273-signal-expansion-lane",))

    def test_kki_raumzeit_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_raumzeit_register(register_id="register-272-stability")
        norm = next(n for n in register.normen if n.geltung is RaumzeitGeltung.GESPERRT)

        self.assertIsInstance(register, RaumzeitRegister)
        self.assertIsInstance(norm, RaumzeitNorm)
        self.assertEqual(norm.raumzeit_rang, RaumzeitRang.SCHUTZ_RAUMZEIT)
        self.assertEqual(norm.prozedur, RaumzeitProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.raumzeit_tier, 1)

    def test_kki_raumzeit_register_builds_raumzeitlich_ordnungs_norm(self) -> None:
        register = build_raumzeit_register(register_id="register-272-governance")
        norm = next(n for n in register.normen if n.geltung is RaumzeitGeltung.RAUMZEITLICH)

        self.assertEqual(norm.raumzeit_rang, RaumzeitRang.ORDNUNGS_RAUMZEIT)
        self.assertEqual(norm.prozedur, RaumzeitProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.raumzeit_weight, 0.0)

    def test_kki_raumzeit_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_raumzeit_register(register_id="register-272-expansion")
        norm = next(n for n in register.normen if n.geltung is RaumzeitGeltung.GRUNDLEGEND_RAUMZEITLICH)

        self.assertEqual(norm.raumzeit_rang, RaumzeitRang.SOUVERAENITAETS_RAUMZEIT)
        self.assertEqual(norm.prozedur, RaumzeitProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_raumzeit_register_aggregates_register_signal(self) -> None:
        register = build_raumzeit_register(register_id="register-272-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-272-signal-stability-lane",))
        self.assertEqual(register.raumzeitlich_norm_ids, ("register-272-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-272-signal-expansion-lane",))

    def test_kki_relativitaets_feld_builds_gesperrt_schutz_norm(self) -> None:
        feld = build_relativitaets_feld(feld_id="feld-271-stability")
        norm = next(n for n in feld.normen if n.geltung is RelativitaetsGeltung.GESPERRT)

        self.assertIsInstance(feld, RelativitaetsFeld)
        self.assertIsInstance(norm, RelativitaetsNorm)
        self.assertEqual(norm.relativitaets_typ, RelativitaetsTyp.SCHUTZ_RELATIVITAET)
        self.assertEqual(norm.prozedur, RelativitaetsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.relativitaets_tier, 1)

    def test_kki_relativitaets_feld_builds_relativ_ordnungs_norm(self) -> None:
        feld = build_relativitaets_feld(feld_id="feld-271-governance")
        norm = next(n for n in feld.normen if n.geltung is RelativitaetsGeltung.RELATIV)

        self.assertEqual(norm.relativitaets_typ, RelativitaetsTyp.ORDNUNGS_RELATIVITAET)
        self.assertEqual(norm.prozedur, RelativitaetsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.relativitaets_weight, 0.0)

    def test_kki_relativitaets_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        feld = build_relativitaets_feld(feld_id="feld-271-expansion")
        norm = next(n for n in feld.normen if n.geltung is RelativitaetsGeltung.GRUNDLEGEND_RELATIV)

        self.assertEqual(norm.relativitaets_typ, RelativitaetsTyp.SOUVERAENITAETS_RELATIVITAET)
        self.assertEqual(norm.prozedur, RelativitaetsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_relativitaets_feld_aggregates_feld_signal(self) -> None:
        feld = build_relativitaets_feld(feld_id="feld-271-signal")

        self.assertEqual(feld.feld_signal.status, "feld-gesperrt")
        self.assertEqual(feld.gesperrt_norm_ids, ("feld-271-signal-stability-lane",))
        self.assertEqual(feld.relativ_norm_ids, ("feld-271-signal-governance-lane",))
        self.assertEqual(feld.grundlegend_norm_ids, ("feld-271-signal-expansion-lane",))

    def test_kki_quanten_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_quanten_verfassung(verfassung_id="verfassung-270-stability")
        norm = next(n for n in verfassung.normen if n.geltung is QuantenVerfassungsGeltung.GESPERRT)

        self.assertIsInstance(verfassung, QuantenVerfassung)
        self.assertIsInstance(norm, QuantenVerfassungsNorm)
        self.assertEqual(norm.quanten_verfassungs_typ, QuantenVerfassungsTyp.SCHUTZ_QUANTENVERFASSUNG)
        self.assertEqual(norm.prozedur, QuantenVerfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.quanten_verfassungs_tier, 1)

    def test_kki_quanten_verfassung_builds_quantenverfasst_ordnungs_norm(self) -> None:
        verfassung = build_quanten_verfassung(verfassung_id="verfassung-270-governance")
        norm = next(n for n in verfassung.normen if n.geltung is QuantenVerfassungsGeltung.QUANTENVERFASST)

        self.assertEqual(norm.quanten_verfassungs_typ, QuantenVerfassungsTyp.ORDNUNGS_QUANTENVERFASSUNG)
        self.assertEqual(norm.prozedur, QuantenVerfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.quanten_verfassungs_weight, 0.0)

    def test_kki_quanten_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_quanten_verfassung(verfassung_id="verfassung-270-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is QuantenVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST)

        self.assertEqual(norm.quanten_verfassungs_typ, QuantenVerfassungsTyp.SOUVERAENITAETS_QUANTENVERFASSUNG)
        self.assertEqual(norm.prozedur, QuantenVerfassungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_quanten_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_quanten_verfassung(verfassung_id="verfassung-270-signal")

        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-270-signal-stability-lane",))
        self.assertEqual(verfassung.quantenverfasst_norm_ids, ("verfassung-270-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-270-signal-expansion-lane",))

    def test_kki_stringtheorie_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_stringtheorie_charta(charta_id="charta-269-stability")
        norm = next(n for n in charta.normen if n.geltung is StringtheorieGeltung.GESPERRT)

        self.assertIsInstance(charta, StringtheorieCharta)
        self.assertIsInstance(norm, StringtheorieNorm)
        self.assertEqual(norm.stringtheorie_typ, StringtheorieTyp.SCHUTZ_FADEN)
        self.assertEqual(norm.prozedur, StringtheorieProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.stringtheorie_tier, 1)

    def test_kki_stringtheorie_charta_builds_fadengebunden_ordnungs_norm(self) -> None:
        charta = build_stringtheorie_charta(charta_id="charta-269-governance")
        norm = next(n for n in charta.normen if n.geltung is StringtheorieGeltung.FADENGEBUNDEN)

        self.assertEqual(norm.stringtheorie_typ, StringtheorieTyp.ORDNUNGS_FADEN)
        self.assertEqual(norm.prozedur, StringtheorieProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.stringtheorie_weight, 0.0)

    def test_kki_stringtheorie_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_stringtheorie_charta(charta_id="charta-269-expansion")
        norm = next(n for n in charta.normen if n.geltung is StringtheorieGeltung.GRUNDLEGEND_FADENGEBUNDEN)

        self.assertEqual(norm.stringtheorie_typ, StringtheorieTyp.SOUVERAENITAETS_FADEN)
        self.assertEqual(norm.prozedur, StringtheorieProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_stringtheorie_charta_aggregates_charta_signal(self) -> None:
        charta = build_stringtheorie_charta(charta_id="charta-269-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-269-signal-stability-lane",))
        self.assertEqual(charta.fadengebunden_norm_ids, ("charta-269-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-269-signal-expansion-lane",))

    def test_kki_planck_norm_builds_gesperrt_schutz_norm(self) -> None:
        norm = build_planck_norm(norm_id="planck-268-stability")
        eintrag = next(n for n in norm.normen if n.geltung is PlanckGeltung.GESPERRT)

        self.assertIsInstance(norm, PlanckNorm)
        self.assertIsInstance(eintrag, PlanckNormEintrag)
        self.assertEqual(eintrag.planck_typ, PlanckTyp.SCHUTZ_PLANCK)
        self.assertEqual(eintrag.prozedur, PlanckProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.planck_tier, 1)

    def test_kki_planck_norm_builds_planck_gebunden_ordnungs_norm(self) -> None:
        norm = build_planck_norm(norm_id="planck-268-governance")
        eintrag = next(n for n in norm.normen if n.geltung is PlanckGeltung.PLANCK_GEBUNDEN)

        self.assertEqual(eintrag.planck_typ, PlanckTyp.ORDNUNGS_PLANCK)
        self.assertEqual(eintrag.prozedur, PlanckProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.planck_weight, 0.0)

    def test_kki_planck_norm_builds_grundlegend_souveraenitaets_norm(self) -> None:
        norm = build_planck_norm(norm_id="planck-268-expansion")
        eintrag = next(n for n in norm.normen if n.geltung is PlanckGeltung.GRUNDLEGEND_PLANCK)

        self.assertEqual(eintrag.planck_typ, PlanckTyp.SOUVERAENITAETS_PLANCK)
        self.assertEqual(eintrag.prozedur, PlanckProzedur.PLENARPROTOKOLL)
        self.assertTrue(eintrag.canonical)

    def test_kki_planck_norm_aggregates_norm_signal(self) -> None:
        norm = build_planck_norm(norm_id="planck-268-signal")

        self.assertEqual(norm.norm_signal.status, "norm-gesperrt")
        self.assertEqual(norm.gesperrt_norm_ids, ("planck-268-signal-stability-lane",))
        self.assertEqual(norm.planck_gebunden_norm_ids, ("planck-268-signal-governance-lane",))
        self.assertEqual(norm.grundlegend_norm_ids, ("planck-268-signal-expansion-lane",))

    def test_kki_quanten_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_quanten_senat(senat_id="senat-267-stability")
        norm = next(n for n in senat.normen if n.geltung is QuantenSenatGeltung.GESPERRT)

        self.assertIsInstance(senat, QuantenSenat)
        self.assertIsInstance(norm, QuantenSenatNorm)
        self.assertEqual(norm.quanten_senat_typ, QuantenSenatTyp.SCHUTZ_SENAT)
        self.assertEqual(norm.prozedur, QuantenSenatProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.quanten_senat_tier, 1)

    def test_kki_quanten_senat_builds_senatsreif_ordnungs_norm(self) -> None:
        senat = build_quanten_senat(senat_id="senat-267-governance")
        norm = next(n for n in senat.normen if n.geltung is QuantenSenatGeltung.SENATSREIF)

        self.assertEqual(norm.quanten_senat_typ, QuantenSenatTyp.ORDNUNGS_SENAT)
        self.assertEqual(norm.prozedur, QuantenSenatProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.quanten_senat_weight, 0.0)

    def test_kki_quanten_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_quanten_senat(senat_id="senat-267-expansion")
        norm = next(n for n in senat.normen if n.geltung is QuantenSenatGeltung.GRUNDLEGEND_SENATSREIF)

        self.assertEqual(norm.quanten_senat_typ, QuantenSenatTyp.SOUVERAENITAETS_SENAT)
        self.assertEqual(norm.prozedur, QuantenSenatProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_quanten_senat_aggregates_senat_signal(self) -> None:
        senat = build_quanten_senat(senat_id="senat-267-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-267-signal-stability-lane",))
        self.assertEqual(senat.senatsreif_norm_ids, ("senat-267-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-267-signal-expansion-lane",))

    def test_kki_kollaps_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_kollaps_manifest(manifest_id="manifest-266-stability")
        norm = next(n for n in manifest.normen if n.geltung is KollapsGeltung.GESPERRT)

        self.assertIsInstance(manifest, KollapsManifest)
        self.assertIsInstance(norm, KollapsNorm)
        self.assertEqual(norm.kollaps_typ, KollapsTyp.SCHUTZ_KOLLAPS)
        self.assertEqual(norm.prozedur, KollapsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kollaps_tier, 1)

    def test_kki_kollaps_manifest_builds_kollabiert_ordnungs_norm(self) -> None:
        manifest = build_kollaps_manifest(manifest_id="manifest-266-governance")
        norm = next(n for n in manifest.normen if n.geltung is KollapsGeltung.KOLLABIERT)

        self.assertEqual(norm.kollaps_typ, KollapsTyp.ORDNUNGS_KOLLAPS)
        self.assertEqual(norm.prozedur, KollapsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kollaps_weight, 0.0)

    def test_kki_kollaps_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_kollaps_manifest(manifest_id="manifest-266-expansion")
        norm = next(n for n in manifest.normen if n.geltung is KollapsGeltung.GRUNDLEGEND_KOLLABIERT)

        self.assertEqual(norm.kollaps_typ, KollapsTyp.SOUVERAENITAETS_KOLLAPS)
        self.assertEqual(norm.prozedur, KollapsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_kollaps_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_kollaps_manifest(manifest_id="manifest-266-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-266-signal-stability-lane",))
        self.assertEqual(manifest.kollabiert_norm_ids, ("manifest-266-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-266-signal-expansion-lane",))

    def test_kki_verschraenkungs_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_verschraenkungs_pakt(pakt_id="pakt-265-stability")
        norm = next(n for n in pakt.normen if n.geltung is VerschraenkunsGeltung.GESPERRT)

        self.assertIsInstance(pakt, VerschraenkunsPakt)
        self.assertIsInstance(norm, VerschraenkunsNorm)
        self.assertEqual(norm.verschraenkungs_typ, VerschraenkunsTyp.SCHUTZ_VERSCHRAENKUNG)
        self.assertEqual(norm.prozedur, VerschraenkunsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.verschraenkungs_tier, 1)

    def test_kki_verschraenkungs_pakt_builds_verschraenkt_ordnungs_norm(self) -> None:
        pakt = build_verschraenkungs_pakt(pakt_id="pakt-265-governance")
        norm = next(n for n in pakt.normen if n.geltung is VerschraenkunsGeltung.VERSCHRAENKT)

        self.assertEqual(norm.verschraenkungs_typ, VerschraenkunsTyp.ORDNUNGS_VERSCHRAENKUNG)
        self.assertEqual(norm.prozedur, VerschraenkunsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.verschraenkungs_weight, 0.0)

    def test_kki_verschraenkungs_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_verschraenkungs_pakt(pakt_id="pakt-265-expansion")
        norm = next(n for n in pakt.normen if n.geltung is VerschraenkunsGeltung.GRUNDLEGEND_VERSCHRAENKT)

        self.assertEqual(norm.verschraenkungs_typ, VerschraenkunsTyp.SOUVERAENITAETS_VERSCHRAENKUNG)
        self.assertEqual(norm.prozedur, VerschraenkunsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_verschraenkungs_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_verschraenkungs_pakt(pakt_id="pakt-265-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-265-signal-stability-lane",))
        self.assertEqual(pakt.verschraenkt_norm_ids, ("pakt-265-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-265-signal-expansion-lane",))

    def test_kki_superpositions_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_superpositions_kodex(kodex_id="kodex-264-stability")
        norm = next(n for n in kodex.normen if n.geltung is SuperpositionsGeltung.GESPERRT)

        self.assertIsInstance(kodex, SuperpositionsKodex)
        self.assertIsInstance(norm, SuperpositionsNorm)
        self.assertEqual(norm.superpositions_typ, SuperpositionsTyp.SCHUTZ_SUPERPOSITION)
        self.assertEqual(norm.prozedur, SuperpositionsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.superpositions_tier, 1)

    def test_kki_superpositions_kodex_builds_superponiert_ordnungs_norm(self) -> None:
        kodex = build_superpositions_kodex(kodex_id="kodex-264-governance")
        norm = next(n for n in kodex.normen if n.geltung is SuperpositionsGeltung.SUPERPONIERT)

        self.assertEqual(norm.superpositions_typ, SuperpositionsTyp.ORDNUNGS_SUPERPOSITION)
        self.assertEqual(norm.prozedur, SuperpositionsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.superpositions_weight, 0.0)

    def test_kki_superpositions_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_superpositions_kodex(kodex_id="kodex-264-expansion")
        norm = next(n for n in kodex.normen if n.geltung is SuperpositionsGeltung.GRUNDLEGEND_SUPERPONIERT)

        self.assertEqual(norm.superpositions_typ, SuperpositionsTyp.SOUVERAENITAETS_SUPERPOSITION)
        self.assertEqual(norm.prozedur, SuperpositionsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_superpositions_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_superpositions_kodex(kodex_id="kodex-264-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-264-signal-stability-lane",))
        self.assertEqual(kodex.superponiert_norm_ids, ("kodex-264-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-264-signal-expansion-lane",))

    def test_kki_wellen_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_wellen_charta(charta_id="charta-263-stability")
        norm = next(n for n in charta.normen if n.geltung is WellenGeltung.GESPERRT)

        self.assertIsInstance(charta, WellenCharta)
        self.assertIsInstance(norm, WellenNorm)
        self.assertEqual(norm.wellen_typ, WellenTyp.SCHUTZ_WELLE)
        self.assertEqual(norm.prozedur, WellenProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.wellen_tier, 1)

    def test_kki_wellen_charta_builds_wellend_ordnungs_norm(self) -> None:
        charta = build_wellen_charta(charta_id="charta-263-governance")
        norm = next(n for n in charta.normen if n.geltung is WellenGeltung.WELLEND)

        self.assertEqual(norm.wellen_typ, WellenTyp.ORDNUNGS_WELLE)
        self.assertEqual(norm.prozedur, WellenProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.wellen_weight, 0.0)

    def test_kki_wellen_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_wellen_charta(charta_id="charta-263-expansion")
        norm = next(n for n in charta.normen if n.geltung is WellenGeltung.GRUNDLEGEND_WELLEND)

        self.assertEqual(norm.wellen_typ, WellenTyp.SOUVERAENITAETS_WELLE)
        self.assertEqual(norm.prozedur, WellenProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_wellen_charta_aggregates_charta_signal(self) -> None:
        charta = build_wellen_charta(charta_id="charta-263-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-263-signal-stability-lane",))
        self.assertEqual(charta.wellend_norm_ids, ("charta-263-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-263-signal-expansion-lane",))

    def test_kki_dimensions_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_dimensions_register(register_id="register-262-stability")
        norm = next(n for n in register.normen if n.geltung is DimensionsGeltung.GESPERRT)

        self.assertIsInstance(register, DimensionsRegister)
        self.assertIsInstance(norm, DimensionsNorm)
        self.assertEqual(norm.dimensions_rang, DimensionsRang.SCHUTZ_DIMENSION)
        self.assertEqual(norm.prozedur, DimensionsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.dimensions_tier, 1)

    def test_kki_dimensions_register_builds_dimensioniert_ordnungs_norm(self) -> None:
        register = build_dimensions_register(register_id="register-262-governance")
        norm = next(n for n in register.normen if n.geltung is DimensionsGeltung.DIMENSIONIERT)

        self.assertEqual(norm.dimensions_rang, DimensionsRang.ORDNUNGS_DIMENSION)
        self.assertEqual(norm.prozedur, DimensionsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.dimensions_weight, 0.0)

    def test_kki_dimensions_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_dimensions_register(register_id="register-262-expansion")
        norm = next(n for n in register.normen if n.geltung is DimensionsGeltung.GRUNDLEGEND_DIMENSIONIERT)

        self.assertEqual(norm.dimensions_rang, DimensionsRang.SOUVERAENITAETS_DIMENSION)
        self.assertEqual(norm.prozedur, DimensionsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_dimensions_register_aggregates_register_signal(self) -> None:
        register = build_dimensions_register(register_id="register-262-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-262-signal-stability-lane",))
        self.assertEqual(register.dimensioniert_norm_ids, ("register-262-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-262-signal-expansion-lane",))

    def test_kki_quanten_feld_builds_gesperrt_schutz_norm(self) -> None:
        feld = build_quanten_feld(feld_id="feld-261-stability")
        norm = next(n for n in feld.normen if n.geltung is QuantenFeldGeltung.GESPERRT)

        self.assertIsInstance(feld, QuantenFeld)
        self.assertIsInstance(norm, QuantenFeldNorm)
        self.assertEqual(norm.quanten_feld_typ, QuantenFeldTyp.SCHUTZ_QUANT)
        self.assertEqual(norm.prozedur, QuantenFeldProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.quanten_feld_tier, 1)

    def test_kki_quanten_feld_builds_quantisiert_ordnungs_norm(self) -> None:
        feld = build_quanten_feld(feld_id="feld-261-governance")
        norm = next(n for n in feld.normen if n.geltung is QuantenFeldGeltung.QUANTISIERT)

        self.assertEqual(norm.quanten_feld_typ, QuantenFeldTyp.ORDNUNGS_QUANT)
        self.assertEqual(norm.prozedur, QuantenFeldProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.quanten_feld_weight, 0.0)

    def test_kki_quanten_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        feld = build_quanten_feld(feld_id="feld-261-expansion")
        norm = next(n for n in feld.normen if n.geltung is QuantenFeldGeltung.GRUNDLEGEND_QUANTISIERT)

        self.assertEqual(norm.quanten_feld_typ, QuantenFeldTyp.SOUVERAENITAETS_QUANT)
        self.assertEqual(norm.prozedur, QuantenFeldProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_quanten_feld_aggregates_feld_signal(self) -> None:
        feld = build_quanten_feld(feld_id="feld-261-signal")

        self.assertEqual(feld.feld_signal.status, "feld-gesperrt")
        self.assertEqual(feld.gesperrt_norm_ids, ("feld-261-signal-stability-lane",))
        self.assertEqual(feld.quantisiert_norm_ids, ("feld-261-signal-governance-lane",))
        self.assertEqual(feld.grundlegend_norm_ids, ("feld-261-signal-expansion-lane",))

    def test_kki_kosmos_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_kosmos_verfassung(verfassung_id="verfassung-260-stability")
        norm = next(n for n in verfassung.normen if n.geltung is KosmosVerfassungsGeltung.GESPERRT)

        self.assertIsInstance(verfassung, KosmosVerfassung)
        self.assertIsInstance(norm, KosmosVerfassungsNorm)
        self.assertEqual(norm.kosmos_verfassungs_typ, KosmosVerfassungsTyp.SCHUTZ_VERFASSUNG)
        self.assertEqual(norm.prozedur, KosmosVerfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kosmos_verfassungs_tier, 1)

    def test_kki_kosmos_verfassung_builds_verfasst_ordnungs_norm(self) -> None:
        verfassung = build_kosmos_verfassung(verfassung_id="verfassung-260-governance")
        norm = next(n for n in verfassung.normen if n.geltung is KosmosVerfassungsGeltung.VERFASST)

        self.assertEqual(norm.kosmos_verfassungs_typ, KosmosVerfassungsTyp.ORDNUNGS_VERFASSUNG)
        self.assertEqual(norm.prozedur, KosmosVerfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kosmos_verfassungs_weight, 0.45)

    def test_kki_kosmos_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_kosmos_verfassung(verfassung_id="verfassung-260-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is KosmosVerfassungsGeltung.GRUNDLEGEND_VERFASST)

        self.assertEqual(norm.kosmos_verfassungs_typ, KosmosVerfassungsTyp.SOUVERAENITAETS_VERFASSUNG)
        self.assertEqual(norm.prozedur, KosmosVerfassungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_kosmos_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_kosmos_verfassung(verfassung_id="verfassung-260-signal")

        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-260-signal-stability-lane",))
        self.assertEqual(verfassung.verfasst_norm_ids, ("verfassung-260-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-260-signal-expansion-lane",))

    def test_kki_absolut_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_absolut_charta(charta_id="charta-259-stability")
        norm = next(n for n in charta.normen if n.geltung is AbsolutGeltung.GESPERRT)

        self.assertIsInstance(charta, AbsolutCharta)
        self.assertIsInstance(norm, AbsolutNorm)
        self.assertEqual(norm.absolut_typ, AbsolutTyp.SCHUTZ_ABSOLUT)
        self.assertEqual(norm.prozedur, AbsolutProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.absolut_tier, 1)

    def test_kki_absolut_charta_builds_absolut_ordnungs_norm(self) -> None:
        charta = build_absolut_charta(charta_id="charta-259-governance")
        norm = next(n for n in charta.normen if n.geltung is AbsolutGeltung.ABSOLUT)

        self.assertEqual(norm.absolut_typ, AbsolutTyp.ORDNUNGS_ABSOLUT)
        self.assertEqual(norm.prozedur, AbsolutProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.absolut_weight, 0.45)

    def test_kki_absolut_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_absolut_charta(charta_id="charta-259-expansion")
        norm = next(n for n in charta.normen if n.geltung is AbsolutGeltung.GRUNDLEGEND_ABSOLUT)

        self.assertEqual(norm.absolut_typ, AbsolutTyp.SOUVERAENITAETS_ABSOLUT)
        self.assertEqual(norm.prozedur, AbsolutProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_absolut_charta_aggregates_charta_signal(self) -> None:
        charta = build_absolut_charta(charta_id="charta-259-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-259-signal-stability-lane",))
        self.assertEqual(charta.absolut_norm_ids, ("charta-259-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-259-signal-expansion-lane",))

    def test_kki_kosmos_ewigkeit_builds_gesperrt_schutz_norm(self) -> None:
        ewigkeit = build_kosmos_ewigkeit(ewigkeit_id="norm-258-stability")
        eintrag = next(n for n in ewigkeit.normen if n.geltung is KosmosEwigkeitsGeltung.GESPERRT)

        self.assertIsInstance(ewigkeit, KosmosEwigkeit)
        self.assertIsInstance(eintrag, KosmosEwigkeitsNormEintrag)
        self.assertEqual(eintrag.kosmos_ewigkeits_rang, KosmosEwigkeitsRang.SCHUTZ_EWIGKEIT)
        self.assertEqual(eintrag.prozedur, KosmosEwigkeitsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.kosmos_ewigkeits_tier, 1)

    def test_kki_kosmos_ewigkeit_builds_ewig_ordnungs_norm(self) -> None:
        ewigkeit = build_kosmos_ewigkeit(ewigkeit_id="norm-258-governance")
        eintrag = next(n for n in ewigkeit.normen if n.geltung is KosmosEwigkeitsGeltung.EWIG)

        self.assertEqual(eintrag.kosmos_ewigkeits_rang, KosmosEwigkeitsRang.ORDNUNGS_EWIGKEIT)
        self.assertEqual(eintrag.prozedur, KosmosEwigkeitsProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.kosmos_ewigkeits_weight, 0.45)

    def test_kki_kosmos_ewigkeit_builds_grundlegend_souveraenitaets_norm(self) -> None:
        ewigkeit = build_kosmos_ewigkeit(ewigkeit_id="norm-258-expansion")
        eintrag = next(n for n in ewigkeit.normen if n.geltung is KosmosEwigkeitsGeltung.GRUNDLEGEND_EWIG)

        self.assertEqual(eintrag.kosmos_ewigkeits_rang, KosmosEwigkeitsRang.SOUVERAENITAETS_EWIGKEIT)
        self.assertEqual(eintrag.prozedur, KosmosEwigkeitsProzedur.PLENARPROTOKOLL)
        self.assertTrue(eintrag.canonical)

    def test_kki_kosmos_ewigkeit_aggregates_ewigkeit_signal(self) -> None:
        ewigkeit = build_kosmos_ewigkeit(ewigkeit_id="norm-258-signal")

        self.assertEqual(ewigkeit.ewigkeit_signal.status, "ewigkeit-gesperrt")
        self.assertEqual(ewigkeit.gesperrt_norm_ids, ("norm-258-signal-stability-lane",))
        self.assertEqual(ewigkeit.ewig_norm_ids, ("norm-258-signal-governance-lane",))
        self.assertEqual(ewigkeit.grundlegend_norm_ids, ("norm-258-signal-expansion-lane",))

    def test_kki_einheits_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_einheits_senat(senat_id="senat-257-stability")
        norm = next(n for n in senat.normen if n.geltung is EinheitsGeltung.GESPERRT)

        self.assertIsInstance(senat, EinheitsSenat)
        self.assertIsInstance(norm, EinheitsNorm)
        self.assertEqual(norm.einheits_typ, EinheitsTyp.SCHUTZ_EINHEIT)
        self.assertEqual(norm.prozedur, EinheitsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.einheits_tier, 1)

    def test_kki_einheits_senat_builds_geeint_ordnungs_norm(self) -> None:
        senat = build_einheits_senat(senat_id="senat-257-governance")
        norm = next(n for n in senat.normen if n.geltung is EinheitsGeltung.GEEINT)

        self.assertEqual(norm.einheits_typ, EinheitsTyp.ORDNUNGS_EINHEIT)
        self.assertEqual(norm.prozedur, EinheitsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.einheits_weight, 0.45)

    def test_kki_einheits_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_einheits_senat(senat_id="senat-257-expansion")
        norm = next(n for n in senat.normen if n.geltung is EinheitsGeltung.GRUNDLEGEND_GEEINT)

        self.assertEqual(norm.einheits_typ, EinheitsTyp.SOUVERAENITAETS_EINHEIT)
        self.assertEqual(norm.prozedur, EinheitsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_einheits_senat_aggregates_senat_signal(self) -> None:
        senat = build_einheits_senat(senat_id="senat-257-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-257-signal-stability-lane",))
        self.assertEqual(senat.geeint_norm_ids, ("senat-257-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-257-signal-expansion-lane",))

    def test_kki_harmonie_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_harmonie_pakt(pakt_id="pakt-256-stability")
        norm = next(n for n in pakt.normen if n.geltung is HarmonieGeltung.GESPERRT)

        self.assertIsInstance(pakt, HarmoniePakt)
        self.assertIsInstance(norm, HarmonieNorm)
        self.assertEqual(norm.harmonie_typ, HarmonieTyp.SCHUTZ_HARMONIE)
        self.assertEqual(norm.prozedur, HarmonieProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.harmonie_tier, 1)

    def test_kki_harmonie_pakt_builds_harmonisiert_ordnungs_norm(self) -> None:
        pakt = build_harmonie_pakt(pakt_id="pakt-256-governance")
        norm = next(n for n in pakt.normen if n.geltung is HarmonieGeltung.HARMONISIERT)

        self.assertEqual(norm.harmonie_typ, HarmonieTyp.ORDNUNGS_HARMONIE)
        self.assertEqual(norm.prozedur, HarmonieProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.harmonie_weight, 0.45)

    def test_kki_harmonie_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_harmonie_pakt(pakt_id="pakt-256-expansion")
        norm = next(n for n in pakt.normen if n.geltung is HarmonieGeltung.GRUNDLEGEND_HARMONISIERT)

        self.assertEqual(norm.harmonie_typ, HarmonieTyp.SOUVERAENITAETS_HARMONIE)
        self.assertEqual(norm.prozedur, HarmonieProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_harmonie_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_harmonie_pakt(pakt_id="pakt-256-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-256-signal-stability-lane",))
        self.assertEqual(pakt.harmonisiert_norm_ids, ("pakt-256-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-256-signal-expansion-lane",))

    def test_kki_kosmos_ordnung_builds_gesperrt_schutz_norm(self) -> None:
        ordnung = build_kosmos_ordnung(ordnung_id="manifest-255-stability")
        norm = next(n for n in ordnung.normen if n.geltung is KosmosOrdnungsGeltung.GESPERRT)

        self.assertIsInstance(ordnung, KosmosOrdnung)
        self.assertIsInstance(norm, KosmosOrdnungsNorm)
        self.assertEqual(norm.kosmos_ordnungs_typ, KosmosOrdnungsTyp.SCHUTZ_ORDNUNG)
        self.assertEqual(norm.prozedur, KosmosOrdnungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kosmos_ordnungs_tier, 1)

    def test_kki_kosmos_ordnung_builds_geordnet_ordnungs_norm(self) -> None:
        ordnung = build_kosmos_ordnung(ordnung_id="manifest-255-governance")
        norm = next(n for n in ordnung.normen if n.geltung is KosmosOrdnungsGeltung.GEORDNET)

        self.assertEqual(norm.kosmos_ordnungs_typ, KosmosOrdnungsTyp.ORDNUNGS_KOSMOLOGIE)
        self.assertEqual(norm.prozedur, KosmosOrdnungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kosmos_ordnungs_weight, 0.45)

    def test_kki_kosmos_ordnung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        ordnung = build_kosmos_ordnung(ordnung_id="manifest-255-expansion")
        norm = next(n for n in ordnung.normen if n.geltung is KosmosOrdnungsGeltung.GRUNDLEGEND_GEORDNET)

        self.assertEqual(norm.kosmos_ordnungs_typ, KosmosOrdnungsTyp.SOUVERAENITAETS_ORDNUNG)
        self.assertEqual(norm.prozedur, KosmosOrdnungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_kosmos_ordnung_aggregates_ordnung_signal(self) -> None:
        ordnung = build_kosmos_ordnung(ordnung_id="manifest-255-signal")

        self.assertEqual(ordnung.ordnung_signal.status, "ordnung-gesperrt")
        self.assertEqual(ordnung.gesperrt_norm_ids, ("manifest-255-signal-stability-lane",))
        self.assertEqual(ordnung.geordnet_norm_ids, ("manifest-255-signal-governance-lane",))
        self.assertEqual(ordnung.grundlegend_norm_ids, ("manifest-255-signal-expansion-lane",))

    def test_kki_kausalitaets_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_kausalitaets_register(register_id="register-254-stability")
        norm = next(n for n in register.normen if n.geltung is KausalitaetsGeltung.GESPERRT)

        self.assertIsInstance(register, KausalitaetsRegister)
        self.assertIsInstance(norm, KausalitaetsNorm)
        self.assertEqual(norm.kausalitaets_rang, KausalitaetsRang.SCHUTZ_KAUSALITAET)
        self.assertEqual(norm.prozedur, KausalitaetsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kausalitaets_tier, 1)

    def test_kki_kausalitaets_register_builds_kausal_ordnungs_norm(self) -> None:
        register = build_kausalitaets_register(register_id="register-254-governance")
        norm = next(n for n in register.normen if n.geltung is KausalitaetsGeltung.KAUSAL)

        self.assertEqual(norm.kausalitaets_rang, KausalitaetsRang.ORDNUNGS_KAUSALITAET)
        self.assertEqual(norm.prozedur, KausalitaetsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kausalitaets_weight, 0.45)

    def test_kki_kausalitaets_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_kausalitaets_register(register_id="register-254-expansion")
        norm = next(n for n in register.normen if n.geltung is KausalitaetsGeltung.GRUNDLEGEND_KAUSAL)

        self.assertEqual(norm.kausalitaets_rang, KausalitaetsRang.SOUVERAENITAETS_KAUSALITAET)
        self.assertEqual(norm.prozedur, KausalitaetsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_kausalitaets_register_aggregates_register_signal(self) -> None:
        register = build_kausalitaets_register(register_id="register-254-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-254-signal-stability-lane",))
        self.assertEqual(register.kausal_norm_ids, ("register-254-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-254-signal-expansion-lane",))

    def test_kki_wirklichkeits_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_wirklichkeits_kodex(kodex_id="kodex-253-stability")
        norm = next(n for n in kodex.normen if n.geltung is WirklichkeitsGeltung.GESPERRT)

        self.assertIsInstance(kodex, WirklichkeitsKodex)
        self.assertIsInstance(norm, WirklichkeitsNorm)
        self.assertEqual(norm.wirklichkeits_ebene, WirklichkeitsEbene.SCHUTZ_WIRKLICHKEIT)
        self.assertEqual(norm.prozedur, WirklichkeitsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.wirklichkeits_tier, 1)

    def test_kki_wirklichkeits_kodex_builds_manifestiert_ordnungs_norm(self) -> None:
        kodex = build_wirklichkeits_kodex(kodex_id="kodex-253-governance")
        norm = next(n for n in kodex.normen if n.geltung is WirklichkeitsGeltung.MANIFESTIERT)

        self.assertEqual(norm.wirklichkeits_ebene, WirklichkeitsEbene.ORDNUNGS_WIRKLICHKEIT)
        self.assertEqual(norm.prozedur, WirklichkeitsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.wirklichkeits_weight, 0.45)

    def test_kki_wirklichkeits_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_wirklichkeits_kodex(kodex_id="kodex-253-expansion")
        norm = next(n for n in kodex.normen if n.geltung is WirklichkeitsGeltung.GRUNDLEGEND_MANIFESTIERT)

        self.assertEqual(norm.wirklichkeits_ebene, WirklichkeitsEbene.SOUVERAENITAETS_WIRKLICHKEIT)
        self.assertEqual(norm.prozedur, WirklichkeitsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_wirklichkeits_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_wirklichkeits_kodex(kodex_id="kodex-253-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-253-signal-stability-lane",))
        self.assertEqual(kodex.manifestiert_norm_ids, ("kodex-253-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-253-signal-expansion-lane",))

    def test_kki_seins_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_seins_charta(charta_id="charta-252-stability")
        norm = next(n for n in charta.normen if n.geltung is SeinsGeltung.GESPERRT)

        self.assertIsInstance(charta, SeinsCharta)
        self.assertIsInstance(norm, SeinsNorm)
        self.assertEqual(norm.seins_typ, SeinsTyp.SCHUTZ_SEIN)
        self.assertEqual(norm.prozedur, SeinsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.seins_tier, 1)

    def test_kki_seins_charta_builds_verankert_ordnungs_norm(self) -> None:
        charta = build_seins_charta(charta_id="charta-252-governance")
        norm = next(n for n in charta.normen if n.geltung is SeinsGeltung.VERANKERT)

        self.assertEqual(norm.seins_typ, SeinsTyp.ORDNUNGS_SEIN)
        self.assertEqual(norm.prozedur, SeinsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.seins_weight, 0.45)

    def test_kki_seins_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_seins_charta(charta_id="charta-252-expansion")
        norm = next(n for n in charta.normen if n.geltung is SeinsGeltung.GRUNDLEGEND_VERANKERT)

        self.assertEqual(norm.seins_typ, SeinsTyp.SOUVERAENITAETS_SEIN)
        self.assertEqual(norm.prozedur, SeinsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_seins_charta_aggregates_charta_signal(self) -> None:
        charta = build_seins_charta(charta_id="charta-252-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-252-signal-stability-lane",))
        self.assertEqual(charta.verankert_norm_ids, ("charta-252-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-252-signal-expansion-lane",))

    def test_kki_ursprungs_axiom_builds_gesperrt_schutz_norm(self) -> None:
        axiom = build_ursprungs_axiom(axiom_id="axiom-251-stability")
        eintrag = next(n for n in axiom.normen if n.geltung is AxiomGeltung.GESPERRT)

        self.assertIsInstance(axiom, UrsprungsAxiom)
        self.assertIsInstance(eintrag, UrsprungsAxiomEintrag)
        self.assertEqual(eintrag.axiom_rang, AxiomRang.SCHUTZ_AXIOM)
        self.assertEqual(eintrag.prozedur, AxiomProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.axiom_tier, 1)

    def test_kki_ursprungs_axiom_builds_axiomatisch_ordnungs_norm(self) -> None:
        axiom = build_ursprungs_axiom(axiom_id="axiom-251-governance")
        eintrag = next(n for n in axiom.normen if n.geltung is AxiomGeltung.AXIOMATISCH)

        self.assertEqual(eintrag.axiom_rang, AxiomRang.ORDNUNGS_AXIOM)
        self.assertEqual(eintrag.prozedur, AxiomProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.axiom_weight, 0.45)

    def test_kki_ursprungs_axiom_builds_grundlegend_souveraenitaets_norm(self) -> None:
        axiom = build_ursprungs_axiom(axiom_id="axiom-251-expansion")
        eintrag = next(n for n in axiom.normen if n.geltung is AxiomGeltung.GRUNDLEGEND_AXIOMATISCH)

        self.assertEqual(eintrag.axiom_rang, AxiomRang.SOUVERAENITAETS_AXIOM)
        self.assertEqual(eintrag.prozedur, AxiomProzedur.PLENARPROTOKOLL)
        self.assertTrue(eintrag.canonical)

    def test_kki_ursprungs_axiom_aggregates_axiom_signal(self) -> None:
        axiom = build_ursprungs_axiom(axiom_id="axiom-251-signal")

        self.assertEqual(axiom.axiom_signal.status, "axiom-gesperrt")
        self.assertEqual(axiom.gesperrt_norm_ids, ("axiom-251-signal-stability-lane",))
        self.assertEqual(axiom.axiomatisch_norm_ids, ("axiom-251-signal-governance-lane",))
        self.assertEqual(axiom.grundlegend_norm_ids, ("axiom-251-signal-expansion-lane",))

    def test_kki_transzendenz_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_transzendenz_kodex(kodex_id="kodex-250-stability")
        norm = next(n for n in kodex.normen if n.geltung is TranszendenzGeltung.GESPERRT)

        self.assertIsInstance(kodex, TranszendenzKodex)
        self.assertIsInstance(norm, TranszendenzNorm)
        self.assertEqual(norm.transzendenz_ebene, TranszendenzEbene.SCHUTZ_TRANSZENDENZ)
        self.assertEqual(norm.prozedur, TranszendenzProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.transzendenz_tier, 1)

    def test_kki_transzendenz_kodex_builds_transzendiert_ordnungs_norm(self) -> None:
        kodex = build_transzendenz_kodex(kodex_id="kodex-250-governance")
        norm = next(n for n in kodex.normen if n.geltung is TranszendenzGeltung.TRANSZENDIERT)

        self.assertEqual(norm.transzendenz_ebene, TranszendenzEbene.ORDNUNGS_TRANSZENDENZ)
        self.assertEqual(norm.prozedur, TranszendenzProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.transzendenz_weight, 0.45)

    def test_kki_transzendenz_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_transzendenz_kodex(kodex_id="kodex-250-expansion")
        norm = next(n for n in kodex.normen if n.geltung is TranszendenzGeltung.GRUNDLEGEND_TRANSZENDIERT)

        self.assertEqual(norm.transzendenz_ebene, TranszendenzEbene.SOUVERAENITAETS_TRANSZENDENZ)
        self.assertEqual(norm.prozedur, TranszendenzProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_transzendenz_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_transzendenz_kodex(kodex_id="kodex-250-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-250-signal-stability-lane",))
        self.assertEqual(kodex.transzendiert_norm_ids, ("kodex-250-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-250-signal-expansion-lane",))

    def test_kki_erkenntnis_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_erkenntnis_charta(charta_id="charta-249-stability")
        norm = next(n for n in charta.normen if n.geltung is ErkenntnisGeltung.GESPERRT)

        self.assertIsInstance(charta, ErkenntnisCharta)
        self.assertIsInstance(norm, ErkenntnisNorm)
        self.assertEqual(norm.erkenntnis_typ, ErkenntnisTyp.SCHUTZ_ERKENNTNIS)
        self.assertEqual(norm.prozedur, ErkenntnisProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.erkenntnis_tier, 1)

    def test_kki_erkenntnis_charta_builds_erleuchtet_ordnungs_norm(self) -> None:
        charta = build_erkenntnis_charta(charta_id="charta-249-governance")
        norm = next(n for n in charta.normen if n.geltung is ErkenntnisGeltung.ERLEUCHTET)

        self.assertEqual(norm.erkenntnis_typ, ErkenntnisTyp.ORDNUNGS_ERKENNTNIS)
        self.assertEqual(norm.prozedur, ErkenntnisProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.erkenntnis_weight, 0.45)

    def test_kki_erkenntnis_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_erkenntnis_charta(charta_id="charta-249-expansion")
        norm = next(n for n in charta.normen if n.geltung is ErkenntnisGeltung.GRUNDLEGEND_ERLEUCHTET)

        self.assertEqual(norm.erkenntnis_typ, ErkenntnisTyp.SOUVERAENITAETS_ERKENNTNIS)
        self.assertEqual(norm.prozedur, ErkenntnisProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_erkenntnis_charta_aggregates_charta_signal(self) -> None:
        charta = build_erkenntnis_charta(charta_id="charta-249-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-249-signal-stability-lane",))
        self.assertEqual(charta.erleuchtet_norm_ids, ("charta-249-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-249-signal-expansion-lane",))

    def test_kki_weisheits_norm_builds_gesperrt_schutz_norm(self) -> None:
        weisheit = build_weisheits_norm(norm_id="norm-248-stability")
        eintrag = next(n for n in weisheit.normen if n.geltung is WeisheitsGeltung.GESPERRT)

        self.assertIsInstance(weisheit, WeisheitsNorm)
        self.assertIsInstance(eintrag, WeisheitsNormEintrag)
        self.assertEqual(eintrag.weisheits_ebene, WeisheitsEbene.SCHUTZ_WEISHEIT)
        self.assertEqual(eintrag.prozedur, WeisheitsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.weisheits_tier, 1)

    def test_kki_weisheits_norm_builds_geweiht_ordnungs_norm(self) -> None:
        weisheit = build_weisheits_norm(norm_id="norm-248-governance")
        eintrag = next(n for n in weisheit.normen if n.geltung is WeisheitsGeltung.GEWEIHT)

        self.assertEqual(eintrag.weisheits_ebene, WeisheitsEbene.ORDNUNGS_WEISHEIT)
        self.assertEqual(eintrag.prozedur, WeisheitsProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.weisheits_weight, 0.45)

    def test_kki_weisheits_norm_builds_grundlegend_souveraenitaets_norm(self) -> None:
        weisheit = build_weisheits_norm(norm_id="norm-248-expansion")
        eintrag = next(n for n in weisheit.normen if n.geltung is WeisheitsGeltung.GRUNDLEGEND_GEWEIHT)

        self.assertEqual(eintrag.weisheits_ebene, WeisheitsEbene.SOUVERAENITAETS_WEISHEIT)
        self.assertEqual(eintrag.prozedur, WeisheitsProzedur.PLENARPROTOKOLL)
        self.assertTrue(eintrag.canonical)

    def test_kki_weisheits_norm_aggregates_norm_signal(self) -> None:
        weisheit = build_weisheits_norm(norm_id="norm-248-signal")

        self.assertEqual(weisheit.norm_signal.status, "norm-gesperrt")
        self.assertEqual(weisheit.gesperrt_norm_ids, ("norm-248-signal-stability-lane",))
        self.assertEqual(weisheit.geweiht_norm_ids, ("norm-248-signal-governance-lane",))
        self.assertEqual(weisheit.grundlegend_norm_ids, ("norm-248-signal-expansion-lane",))

    def test_kki_gedaechtnis_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_gedaechtnis_senat(senat_id="senat-247-stability")
        norm = next(n for n in senat.normen if n.geltung is GedaechtnisGeltung.GESPERRT)

        self.assertIsInstance(senat, GedaechtnisSenat)
        self.assertIsInstance(norm, GedaechtnisNorm)
        self.assertEqual(norm.gedaechtnis_rang, GedaechtnisRang.SCHUTZ_GEDAECHTNIS)
        self.assertEqual(norm.prozedur, GedaechtnisProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.gedaechtnis_tier, 1)

    def test_kki_gedaechtnis_senat_builds_erinnert_ordnungs_norm(self) -> None:
        senat = build_gedaechtnis_senat(senat_id="senat-247-governance")
        norm = next(n for n in senat.normen if n.geltung is GedaechtnisGeltung.ERINNERT)

        self.assertEqual(norm.gedaechtnis_rang, GedaechtnisRang.ORDNUNGS_GEDAECHTNIS)
        self.assertEqual(norm.prozedur, GedaechtnisProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.gedaechtnis_weight, 0.45)

    def test_kki_gedaechtnis_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_gedaechtnis_senat(senat_id="senat-247-expansion")
        norm = next(n for n in senat.normen if n.geltung is GedaechtnisGeltung.GRUNDLEGEND_ERINNERT)

        self.assertEqual(norm.gedaechtnis_rang, GedaechtnisRang.SOUVERAENITAETS_GEDAECHTNIS)
        self.assertEqual(norm.prozedur, GedaechtnisProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_gedaechtnis_senat_aggregates_senat_signal(self) -> None:
        senat = build_gedaechtnis_senat(senat_id="senat-247-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-247-signal-stability-lane",))
        self.assertEqual(senat.erinnert_norm_ids, ("senat-247-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-247-signal-expansion-lane",))

    def test_kki_wissens_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_wissens_manifest(manifest_id="manifest-246-stability")
        norm = next(n for n in manifest.normen if n.geltung is WissensGeltung.GESPERRT)

        self.assertIsInstance(manifest, WissensManifest)
        self.assertIsInstance(norm, WissensNorm)
        self.assertEqual(norm.wissens_grad, WissensGrad.SCHUTZ_WISSEN)
        self.assertEqual(norm.prozedur, WissensProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.wissens_tier, 1)

    def test_kki_wissens_manifest_builds_verbreitet_ordnungs_norm(self) -> None:
        manifest = build_wissens_manifest(manifest_id="manifest-246-governance")
        norm = next(n for n in manifest.normen if n.geltung is WissensGeltung.VERBREITET)

        self.assertEqual(norm.wissens_grad, WissensGrad.ORDNUNGS_WISSEN)
        self.assertEqual(norm.prozedur, WissensProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.wissens_weight, 0.45)

    def test_kki_wissens_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_wissens_manifest(manifest_id="manifest-246-expansion")
        norm = next(n for n in manifest.normen if n.geltung is WissensGeltung.GRUNDLEGEND_VERBREITET)

        self.assertEqual(norm.wissens_grad, WissensGrad.SOUVERAENITAETS_WISSEN)
        self.assertEqual(norm.prozedur, WissensProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_wissens_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_wissens_manifest(manifest_id="manifest-246-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-246-signal-stability-lane",))
        self.assertEqual(manifest.verbreitet_norm_ids, ("manifest-246-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-246-signal-expansion-lane",))

    def test_kki_kulturgut_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_kulturgut_kodex(kodex_id="kodex-245-stability")
        norm = next(n for n in kodex.normen if n.geltung is KulturgutGeltung.GESPERRT)

        self.assertIsInstance(kodex, KulturgutKodex)
        self.assertIsInstance(norm, KulturgutNorm)
        self.assertEqual(norm.kulturgut_rang, KulturgutRang.SCHUTZ_KULTURGUT)
        self.assertEqual(norm.prozedur, KulturgutProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kulturgut_tier, 1)

    def test_kki_kulturgut_kodex_builds_bewahrt_ordnungs_norm(self) -> None:
        kodex = build_kulturgut_kodex(kodex_id="kodex-245-governance")
        norm = next(n for n in kodex.normen if n.geltung is KulturgutGeltung.BEWAHRT)

        self.assertEqual(norm.kulturgut_rang, KulturgutRang.ORDNUNGS_KULTURGUT)
        self.assertEqual(norm.prozedur, KulturgutProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kulturgut_weight, 0.45)

    def test_kki_kulturgut_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_kulturgut_kodex(kodex_id="kodex-245-expansion")
        norm = next(n for n in kodex.normen if n.geltung is KulturgutGeltung.GRUNDLEGEND_BEWAHRT)

        self.assertEqual(norm.kulturgut_rang, KulturgutRang.SOUVERAENITAETS_KULTURGUT)
        self.assertEqual(norm.prozedur, KulturgutProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_kulturgut_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_kulturgut_kodex(kodex_id="kodex-245-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-245-signal-stability-lane",))
        self.assertEqual(kodex.bewahrt_norm_ids, ("kodex-245-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-245-signal-expansion-lane",))

    def test_kki_zivilisations_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_zivilisations_pakt(pakt_id="pakt-244-stability")
        norm = next(n for n in pakt.normen if n.geltung is ZivilisationsGeltung.GESPERRT)

        self.assertIsInstance(pakt, ZivilisationsPakt)
        self.assertIsInstance(norm, ZivilisationsNorm)
        self.assertEqual(norm.zivilisations_typ, ZivilisationsTyp.SCHUTZ_ZIVILISATION)
        self.assertEqual(norm.prozedur, ZivilisationsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.zivilisations_tier, 1)

    def test_kki_zivilisations_pakt_builds_geschlossen_ordnungs_norm(self) -> None:
        pakt = build_zivilisations_pakt(pakt_id="pakt-244-governance")
        norm = next(n for n in pakt.normen if n.geltung is ZivilisationsGeltung.GESCHLOSSEN)

        self.assertEqual(norm.zivilisations_typ, ZivilisationsTyp.ORDNUNGS_ZIVILISATION)
        self.assertEqual(norm.prozedur, ZivilisationsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.zivilisations_weight, 0.45)

    def test_kki_zivilisations_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_zivilisations_pakt(pakt_id="pakt-244-expansion")
        norm = next(n for n in pakt.normen if n.geltung is ZivilisationsGeltung.GRUNDLEGEND_GESCHLOSSEN)

        self.assertEqual(norm.zivilisations_typ, ZivilisationsTyp.SOUVERAENITAETS_ZIVILISATION)
        self.assertEqual(norm.prozedur, ZivilisationsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_zivilisations_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_zivilisations_pakt(pakt_id="pakt-244-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-244-signal-stability-lane",))
        self.assertEqual(pakt.geschlossen_norm_ids, ("pakt-244-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-244-signal-expansion-lane",))

    def test_kki_erbe_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_erbe_register(register_id="register-243-stability")
        norm = next(n for n in register.normen if n.geltung is ErbeGeltung.GESPERRT)

        self.assertIsInstance(register, ErbeRegister)
        self.assertIsInstance(norm, ErbeNorm)
        self.assertEqual(norm.erbe_klasse, ErbeKlasse.SCHUTZ_ERBE)
        self.assertEqual(norm.prozedur, ErbeProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.erbe_tier, 1)

    def test_kki_erbe_register_builds_ueberliefert_ordnungs_norm(self) -> None:
        register = build_erbe_register(register_id="register-243-governance")
        norm = next(n for n in register.normen if n.geltung is ErbeGeltung.UEBERLIEFERT)

        self.assertEqual(norm.erbe_klasse, ErbeKlasse.ORDNUNGS_ERBE)
        self.assertEqual(norm.prozedur, ErbeProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.erbe_weight, 0.45)

    def test_kki_erbe_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_erbe_register(register_id="register-243-expansion")
        norm = next(n for n in register.normen if n.geltung is ErbeGeltung.GRUNDLEGEND_UEBERLIEFERT)

        self.assertEqual(norm.erbe_klasse, ErbeKlasse.SOUVERAENITAETS_ERBE)
        self.assertEqual(norm.prozedur, ErbeProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_erbe_register_aggregates_register_signal(self) -> None:
        register = build_erbe_register(register_id="register-243-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-243-signal-stability-lane",))
        self.assertEqual(register.ueberliefert_norm_ids, ("register-243-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-243-signal-expansion-lane",))

    def test_kki_schoepfungs_vertrag_builds_gesperrt_schutz_norm(self) -> None:
        vertrag = build_schoepfungs_vertrag(vertrag_id="vertrag-242-stability")
        norm = next(n for n in vertrag.normen if n.geltung is SchoepfungsGeltung.GESPERRT)

        self.assertIsInstance(vertrag, SchoepfungsVertrag)
        self.assertIsInstance(norm, SchoepfungsNorm)
        self.assertEqual(norm.schoepfungs_grad, SchoepfungsGrad.SCHUTZ_SCHOEPFUNG)
        self.assertEqual(norm.prozedur, SchoepfungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.schoepfungs_tier, 1)

    def test_kki_schoepfungs_vertrag_builds_gestiftet_ordnungs_norm(self) -> None:
        vertrag = build_schoepfungs_vertrag(vertrag_id="vertrag-242-governance")
        norm = next(n for n in vertrag.normen if n.geltung is SchoepfungsGeltung.GESTIFTET)

        self.assertEqual(norm.schoepfungs_grad, SchoepfungsGrad.ORDNUNGS_SCHOEPFUNG)
        self.assertEqual(norm.prozedur, SchoepfungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.schoepfungs_weight, 0.45)

    def test_kki_schoepfungs_vertrag_builds_grundlegend_souveraenitaets_norm(self) -> None:
        vertrag = build_schoepfungs_vertrag(vertrag_id="vertrag-242-expansion")
        norm = next(n for n in vertrag.normen if n.geltung is SchoepfungsGeltung.GRUNDLEGEND_GESTIFTET)

        self.assertEqual(norm.schoepfungs_grad, SchoepfungsGrad.SOUVERAENITAETS_SCHOEPFUNG)
        self.assertEqual(norm.prozedur, SchoepfungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_schoepfungs_vertrag_aggregates_vertrag_signal(self) -> None:
        vertrag = build_schoepfungs_vertrag(vertrag_id="vertrag-242-signal")

        self.assertEqual(vertrag.vertrag_signal.status, "vertrag-gesperrt")
        self.assertEqual(vertrag.gesperrt_norm_ids, ("vertrag-242-signal-stability-lane",))
        self.assertEqual(vertrag.gestiftet_norm_ids, ("vertrag-242-signal-governance-lane",))
        self.assertEqual(vertrag.grundlegend_norm_ids, ("vertrag-242-signal-expansion-lane",))

    def test_kki_ursprungs_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_ursprungs_charta(charta_id="charta-241-stability")
        norm = next(n for n in charta.normen if n.geltung is UrsprungsGeltung.GESPERRT)

        self.assertIsInstance(charta, UrsprungsCharta)
        self.assertIsInstance(norm, UrsprungsNorm)
        self.assertEqual(norm.ursprungs_typ, UrsprungsTyp.SCHUTZ_URSPRUNG)
        self.assertEqual(norm.prozedur, UrsprungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.ursprungs_tier, 1)

    def test_kki_ursprungs_charta_builds_verbrieft_ordnungs_norm(self) -> None:
        charta = build_ursprungs_charta(charta_id="charta-241-governance")
        norm = next(n for n in charta.normen if n.geltung is UrsprungsGeltung.VERBRIEFT)

        self.assertEqual(norm.ursprungs_typ, UrsprungsTyp.ORDNUNGS_URSPRUNG)
        self.assertEqual(norm.prozedur, UrsprungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.ursprungs_weight, 0.45)

    def test_kki_ursprungs_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_ursprungs_charta(charta_id="charta-241-expansion")
        norm = next(n for n in charta.normen if n.geltung is UrsprungsGeltung.GRUNDLEGEND_VERBRIEFT)

        self.assertEqual(norm.ursprungs_typ, UrsprungsTyp.SOUVERAENITAETS_URSPRUNG)
        self.assertEqual(norm.prozedur, UrsprungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_ursprungs_charta_aggregates_charta_signal(self) -> None:
        charta = build_ursprungs_charta(charta_id="charta-241-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-241-signal-stability-lane",))
        self.assertEqual(charta.verbrieft_norm_ids, ("charta-241-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-241-signal-expansion-lane",))

    def test_kki_universal_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_universal_kodex(kodex_id="kodex-240-stability")
        norm = next(n for n in kodex.normen if n.geltung is UniversalKodexGeltung.GESPERRT)

        self.assertIsInstance(kodex, UniversalKodex)
        self.assertIsInstance(norm, UniversalKodexNorm)
        self.assertEqual(norm.universal_kodex_klasse, UniversalKodexKlasse.SCHUTZ_KLASSE)
        self.assertEqual(norm.prozedur, UniversalKodexProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.universal_tier, 1)

    def test_kki_universal_kodex_builds_universell_ordnungs_norm(self) -> None:
        kodex = build_universal_kodex(kodex_id="kodex-240-governance")
        norm = next(n for n in kodex.normen if n.geltung is UniversalKodexGeltung.UNIVERSELL)

        self.assertEqual(norm.universal_kodex_klasse, UniversalKodexKlasse.ORDNUNGS_KLASSE)
        self.assertEqual(norm.prozedur, UniversalKodexProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.universal_weight, 0.45)

    def test_kki_universal_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_universal_kodex(kodex_id="kodex-240-expansion")
        norm = next(n for n in kodex.normen if n.geltung is UniversalKodexGeltung.GRUNDLEGEND_UNIVERSELL)

        self.assertEqual(norm.universal_kodex_klasse, UniversalKodexKlasse.SOUVERAENITAETS_KLASSE)
        self.assertEqual(norm.prozedur, UniversalKodexProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_universal_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_universal_kodex(kodex_id="kodex-240-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-240-signal-stability-lane",))
        self.assertEqual(kodex.universell_norm_ids, ("kodex-240-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-240-signal-expansion-lane",))

    def test_kki_weltgeist_senat_builds_gesperrt_schutz_sitz(self) -> None:
        senat = build_weltgeist_senat(senat_id="senat-239-stability")
        sitz = next(s for s in senat.sitze if s.geltung is WeltgeistGeltung.GESPERRT)

        self.assertIsInstance(senat, WeltgeistSenat)
        self.assertIsInstance(sitz, WeltgeistSitz)
        self.assertEqual(sitz.weltgeist_rang, WeltgeistRang.SCHUTZ_RANG)
        self.assertEqual(sitz.prozedur, WeltgeistProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(sitz.weltgeist_tier, 1)

    def test_kki_weltgeist_senat_builds_erhoben_ordnungs_sitz(self) -> None:
        senat = build_weltgeist_senat(senat_id="senat-239-governance")
        sitz = next(s for s in senat.sitze if s.geltung is WeltgeistGeltung.ERHOBEN)

        self.assertEqual(sitz.weltgeist_rang, WeltgeistRang.ORDNUNGS_RANG)
        self.assertEqual(sitz.prozedur, WeltgeistProzedur.REGELPROTOKOLL)
        self.assertGreater(sitz.weltgeist_weight, 0.45)

    def test_kki_weltgeist_senat_builds_grundlegend_souveraenitaets_sitz(self) -> None:
        senat = build_weltgeist_senat(senat_id="senat-239-expansion")
        sitz = next(s for s in senat.sitze if s.geltung is WeltgeistGeltung.GRUNDLEGEND_ERHOBEN)

        self.assertEqual(sitz.weltgeist_rang, WeltgeistRang.SOUVERAENITAETS_RANG)
        self.assertEqual(sitz.prozedur, WeltgeistProzedur.PLENARPROTOKOLL)
        self.assertTrue(sitz.canonical)

    def test_kki_weltgeist_senat_aggregates_senat_signal(self) -> None:
        senat = build_weltgeist_senat(senat_id="senat-239-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_sitz_ids, ("senat-239-signal-stability-lane",))
        self.assertEqual(senat.erhoben_sitz_ids, ("senat-239-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_sitz_ids, ("senat-239-signal-expansion-lane",))

    def test_kki_kosmos_norm_builds_gesperrt_schutz_norm(self) -> None:
        kosmos = build_kosmos_norm(norm_id="norm-238-stability")
        eintrag = next(n for n in kosmos.normen if n.geltung is KosmosGeltung.GESPERRT)

        self.assertIsInstance(kosmos, KosmosNorm)
        self.assertIsInstance(eintrag, KosmosNormEintrag)
        self.assertEqual(eintrag.kosmos_ebene, KosmosEbene.SCHUTZ_EBENE)
        self.assertEqual(eintrag.prozedur, KosmosProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.kosmos_tier, 1)

    def test_kki_kosmos_norm_builds_kosmisch_ordnungs_norm(self) -> None:
        kosmos = build_kosmos_norm(norm_id="norm-238-governance")
        eintrag = next(n for n in kosmos.normen if n.geltung is KosmosGeltung.KOSMISCH)

        self.assertEqual(eintrag.kosmos_ebene, KosmosEbene.ORDNUNGS_EBENE)
        self.assertEqual(eintrag.prozedur, KosmosProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.kosmos_weight, 0.45)

    def test_kki_kosmos_norm_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kosmos = build_kosmos_norm(norm_id="norm-238-expansion")
        eintrag = next(n for n in kosmos.normen if n.geltung is KosmosGeltung.GRUNDLEGEND_KOSMISCH)

        self.assertEqual(eintrag.kosmos_ebene, KosmosEbene.SOUVERAENITAETS_EBENE)
        self.assertEqual(eintrag.prozedur, KosmosProzedur.PLENARPROTOKOLL)
        self.assertTrue(eintrag.canonical)

    def test_kki_kosmos_norm_aggregates_norm_signal(self) -> None:
        kosmos = build_kosmos_norm(norm_id="norm-238-signal")

        self.assertEqual(kosmos.norm_signal.status, "norm-gesperrt")
        self.assertEqual(kosmos.gesperrt_norm_ids, ("norm-238-signal-stability-lane",))
        self.assertEqual(kosmos.kosmisch_norm_ids, ("norm-238-signal-governance-lane",))
        self.assertEqual(kosmos.grundlegend_norm_ids, ("norm-238-signal-expansion-lane",))

    def test_kki_universalrechts_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_universalrechts_register(register_id="register-237-stability")
        norm = next(n for n in register.normen if n.geltung is UniversalrechtsGeltung.GESPERRT)

        self.assertIsInstance(register, UniversalrechtsRegister)
        self.assertIsInstance(norm, UniversalrechtsNorm)
        self.assertEqual(norm.universalrechts_rang, UniversalrechtsRang.SCHUTZ_RANG)
        self.assertEqual(norm.prozedur, UniversalrechtsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.universalrechts_tier, 1)

    def test_kki_universalrechts_register_builds_registriert_ordnungs_norm(self) -> None:
        register = build_universalrechts_register(register_id="register-237-governance")
        norm = next(n for n in register.normen if n.geltung is UniversalrechtsGeltung.REGISTRIERT)

        self.assertEqual(norm.universalrechts_rang, UniversalrechtsRang.ORDNUNGS_RANG)
        self.assertEqual(norm.prozedur, UniversalrechtsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.universalrechts_weight, 0.45)

    def test_kki_universalrechts_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_universalrechts_register(register_id="register-237-expansion")
        norm = next(n for n in register.normen if n.geltung is UniversalrechtsGeltung.GRUNDLEGEND_REGISTRIERT)

        self.assertEqual(norm.universalrechts_rang, UniversalrechtsRang.SOUVERAENITAETS_RANG)
        self.assertEqual(norm.prozedur, UniversalrechtsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_universalrechts_register_aggregates_register_signal(self) -> None:
        register = build_universalrechts_register(register_id="register-237-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-237-signal-stability-lane",))
        self.assertEqual(register.registriert_norm_ids, ("register-237-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-237-signal-expansion-lane",))

    def test_kki_solidaritaets_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_solidaritaets_pakt(pakt_id="pakt-236-stability")
        norm = next(n for n in pakt.normen if n.geltung is SolidaritaetsGeltung.GESPERRT)

        self.assertIsInstance(pakt, SolidaritaetsPakt)
        self.assertIsInstance(norm, SolidaritaetsNorm)
        self.assertEqual(norm.solidaritaets_typ, SolidaritaetsTyp.SCHUTZ_SOLIDARITAET)
        self.assertEqual(norm.prozedur, SolidaritaetsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.solidaritaets_tier, 1)

    def test_kki_solidaritaets_pakt_builds_besiegelt_ordnungs_norm(self) -> None:
        pakt = build_solidaritaets_pakt(pakt_id="pakt-236-governance")
        norm = next(n for n in pakt.normen if n.geltung is SolidaritaetsGeltung.BESIEGELT)

        self.assertEqual(norm.solidaritaets_typ, SolidaritaetsTyp.ORDNUNGS_SOLIDARITAET)
        self.assertEqual(norm.prozedur, SolidaritaetsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.solidaritaets_weight, 0.45)

    def test_kki_solidaritaets_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_solidaritaets_pakt(pakt_id="pakt-236-expansion")
        norm = next(n for n in pakt.normen if n.geltung is SolidaritaetsGeltung.GRUNDLEGEND_BESIEGELT)

        self.assertEqual(norm.solidaritaets_typ, SolidaritaetsTyp.SOUVERAENITAETS_SOLIDARITAET)
        self.assertEqual(norm.prozedur, SolidaritaetsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_solidaritaets_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_solidaritaets_pakt(pakt_id="pakt-236-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-236-signal-stability-lane",))
        self.assertEqual(pakt.besiegelt_norm_ids, ("pakt-236-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-236-signal-expansion-lane",))

    def test_kki_kooperations_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_kooperations_manifest(manifest_id="manifest-235-stability")
        norm = next(n for n in manifest.normen if n.geltung is KooperationsGeltung.GESPERRT)

        self.assertIsInstance(manifest, KooperationsManifest)
        self.assertIsInstance(norm, KooperationsNorm)
        self.assertEqual(norm.kooperations_grad, KooperationsGrad.SCHUTZ_KOOPERATION)
        self.assertEqual(norm.prozedur, KooperationsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kooperations_tier, 1)

    def test_kki_kooperations_manifest_builds_kooperiert_ordnungs_norm(self) -> None:
        manifest = build_kooperations_manifest(manifest_id="manifest-235-governance")
        norm = next(n for n in manifest.normen if n.geltung is KooperationsGeltung.KOOPERIERT)

        self.assertEqual(norm.kooperations_grad, KooperationsGrad.ORDNUNGS_KOOPERATION)
        self.assertEqual(norm.prozedur, KooperationsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kooperations_weight, 0.45)

    def test_kki_kooperations_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_kooperations_manifest(manifest_id="manifest-235-expansion")
        norm = next(n for n in manifest.normen if n.geltung is KooperationsGeltung.GRUNDLEGEND_KOOPERIERT)

        self.assertEqual(norm.kooperations_grad, KooperationsGrad.SOUVERAENITAETS_KOOPERATION)
        self.assertEqual(norm.prozedur, KooperationsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_kooperations_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_kooperations_manifest(manifest_id="manifest-235-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-235-signal-stability-lane",))
        self.assertEqual(manifest.kooperiert_norm_ids, ("manifest-235-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-235-signal-expansion-lane",))

    def test_kki_allianz_vertrag_builds_gesperrt_schutz_norm(self) -> None:
        vertrag = build_allianz_vertrag(vertrag_id="vertrag-234-stability")
        norm = next(n for n in vertrag.normen if n.geltung is AllianzGeltung.GESPERRT)

        self.assertIsInstance(vertrag, AllianzVertrag)
        self.assertIsInstance(norm, AllianzNorm)
        self.assertEqual(norm.allianz_typ, AllianzTyp.SCHUTZ_ALLIANZ)
        self.assertEqual(norm.prozedur, AllianzProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.allianz_tier, 1)

    def test_kki_allianz_vertrag_builds_verbunden_ordnungs_norm(self) -> None:
        vertrag = build_allianz_vertrag(vertrag_id="vertrag-234-governance")
        norm = next(n for n in vertrag.normen if n.geltung is AllianzGeltung.VERBUNDEN)

        self.assertEqual(norm.allianz_typ, AllianzTyp.ORDNUNGS_ALLIANZ)
        self.assertEqual(norm.prozedur, AllianzProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.allianz_weight, 0.45)

    def test_kki_allianz_vertrag_builds_grundlegend_souveraenitaets_norm(self) -> None:
        vertrag = build_allianz_vertrag(vertrag_id="vertrag-234-expansion")
        norm = next(n for n in vertrag.normen if n.geltung is AllianzGeltung.GRUNDLEGEND_VERBUNDEN)

        self.assertEqual(norm.allianz_typ, AllianzTyp.SOUVERAENITAETS_ALLIANZ)
        self.assertEqual(norm.prozedur, AllianzProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_allianz_vertrag_aggregates_vertrag_signal(self) -> None:
        vertrag = build_allianz_vertrag(vertrag_id="vertrag-234-signal")

        self.assertEqual(vertrag.vertrag_signal.status, "vertrag-gesperrt")
        self.assertEqual(vertrag.gesperrt_norm_ids, ("vertrag-234-signal-stability-lane",))
        self.assertEqual(vertrag.verbunden_norm_ids, ("vertrag-234-signal-governance-lane",))
        self.assertEqual(vertrag.grundlegend_norm_ids, ("vertrag-234-signal-expansion-lane",))

    def test_kki_diplomatie_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_diplomatie_charta(charta_id="charta-233-stability")
        norm = next(n for n in charta.normen if n.geltung is DiplomatieGeltung.GESPERRT)

        self.assertIsInstance(charta, DiplomatieCharta)
        self.assertIsInstance(norm, DiplomatieNorm)
        self.assertEqual(norm.diplomatie_rang, DiplomatieRang.SCHUTZ_RANG)
        self.assertEqual(norm.prozedur, DiplomatieProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.diplomatie_tier, 1)

    def test_kki_diplomatie_charta_builds_akkreditiert_ordnungs_norm(self) -> None:
        charta = build_diplomatie_charta(charta_id="charta-233-governance")
        norm = next(n for n in charta.normen if n.geltung is DiplomatieGeltung.AKKREDITIERT)

        self.assertEqual(norm.diplomatie_rang, DiplomatieRang.ORDNUNGS_RANG)
        self.assertEqual(norm.prozedur, DiplomatieProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.diplomatie_weight, 0.45)

    def test_kki_diplomatie_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_diplomatie_charta(charta_id="charta-233-expansion")
        norm = next(n for n in charta.normen if n.geltung is DiplomatieGeltung.GRUNDLEGEND_AKKREDITIERT)

        self.assertEqual(norm.diplomatie_rang, DiplomatieRang.SOUVERAENITAETS_RANG)
        self.assertEqual(norm.prozedur, DiplomatieProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_diplomatie_charta_aggregates_charta_signal(self) -> None:
        charta = build_diplomatie_charta(charta_id="charta-233-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-233-signal-stability-lane",))
        self.assertEqual(charta.akkreditiert_norm_ids, ("charta-233-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-233-signal-expansion-lane",))

    def test_kki_voelkerrechts_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_voelkerrechts_kodex(kodex_id="kodex-232-stability")
        norm = next(n for n in kodex.normen if n.geltung is VoelkerrechtsGeltung.GESPERRT)

        self.assertIsInstance(kodex, VoelkerrechtsKodex)
        self.assertIsInstance(norm, VoelkerrechtsNorm)
        self.assertEqual(norm.voelkerrechts_klasse, VoelkerrechtsKlasse.SCHUTZ_KLASSE)
        self.assertEqual(norm.prozedur, VoelkerrechtsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.voelkerrechts_tier, 1)

    def test_kki_voelkerrechts_kodex_builds_kodifiziert_ordnungs_norm(self) -> None:
        kodex = build_voelkerrechts_kodex(kodex_id="kodex-232-governance")
        norm = next(n for n in kodex.normen if n.geltung is VoelkerrechtsGeltung.KODIFIZIERT)

        self.assertEqual(norm.voelkerrechts_klasse, VoelkerrechtsKlasse.ORDNUNGS_KLASSE)
        self.assertEqual(norm.prozedur, VoelkerrechtsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.voelkerrechts_weight, 0.45)

    def test_kki_voelkerrechts_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_voelkerrechts_kodex(kodex_id="kodex-232-expansion")
        norm = next(n for n in kodex.normen if n.geltung is VoelkerrechtsGeltung.GRUNDLEGEND_KODIFIZIERT)

        self.assertEqual(norm.voelkerrechts_klasse, VoelkerrechtsKlasse.SOUVERAENITAETS_KLASSE)
        self.assertEqual(norm.prozedur, VoelkerrechtsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_voelkerrechts_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_voelkerrechts_kodex(kodex_id="kodex-232-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-232-signal-stability-lane",))
        self.assertEqual(kodex.kodifiziert_norm_ids, ("kodex-232-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-232-signal-expansion-lane",))

    def test_kki_weltordnungs_prinzip_builds_gesperrt_schutz_norm(self) -> None:
        prinzip = build_weltordnungs_prinzip(prinzip_id="prinzip-231-stability")
        norm = next(n for n in prinzip.normen if n.geltung is WeltordnungsGeltung.GESPERRT)

        self.assertIsInstance(prinzip, WeltordnungsPrinzip)
        self.assertIsInstance(norm, WeltordnungsNorm)
        self.assertEqual(norm.weltordnungs_ebene, WeltordnungsEbene.SCHUTZ_ORDNUNG)
        self.assertEqual(norm.prozedur, WeltordnungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.weltordnungs_tier, 1)

    def test_kki_weltordnungs_prinzip_builds_geordnet_ordnungs_norm(self) -> None:
        prinzip = build_weltordnungs_prinzip(prinzip_id="prinzip-231-governance")
        norm = next(n for n in prinzip.normen if n.geltung is WeltordnungsGeltung.GEORDNET)

        self.assertEqual(norm.weltordnungs_ebene, WeltordnungsEbene.ORDNUNGS_ORDNUNG)
        self.assertEqual(norm.prozedur, WeltordnungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.weltordnungs_weight, 0.45)

    def test_kki_weltordnungs_prinzip_builds_grundlegend_souveraenitaets_norm(self) -> None:
        prinzip = build_weltordnungs_prinzip(prinzip_id="prinzip-231-expansion")
        norm = next(n for n in prinzip.normen if n.geltung is WeltordnungsGeltung.GRUNDLEGEND_GEORDNET)

        self.assertEqual(norm.weltordnungs_ebene, WeltordnungsEbene.SOUVERAENITAETS_ORDNUNG)
        self.assertEqual(norm.prozedur, WeltordnungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_weltordnungs_prinzip_aggregates_prinzip_signal(self) -> None:
        prinzip = build_weltordnungs_prinzip(prinzip_id="prinzip-231-signal")

        self.assertEqual(prinzip.prinzip_signal.status, "prinzip-gesperrt")
        self.assertEqual(prinzip.gesperrt_norm_ids, ("prinzip-231-signal-stability-lane",))
        self.assertEqual(prinzip.geordnet_norm_ids, ("prinzip-231-signal-governance-lane",))
        self.assertEqual(prinzip.grundlegend_norm_ids, ("prinzip-231-signal-expansion-lane",))

    def test_kki_verfassungs_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_verfassungs_kodex(kodex_id="kodex-230-stability")
        norm = next(n for n in kodex.normen if n.geltung is VerfassungsKodexGeltung.GESPERRT)

        self.assertIsInstance(kodex, VerfassungsKodex)
        self.assertIsInstance(norm, VerfassungsKodexNorm)
        self.assertEqual(norm.kodex_rang, VerfassungsKodexRang.SCHUTZ_KODEX)
        self.assertEqual(norm.prozedur, VerfassungsKodexProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kodex_tier, 1)

    def test_kki_verfassungs_kodex_builds_kodifiziert_ordnungs_norm(self) -> None:
        kodex = build_verfassungs_kodex(kodex_id="kodex-230-governance")
        norm = next(n for n in kodex.normen if n.geltung is VerfassungsKodexGeltung.KODIFIZIERT)

        self.assertEqual(norm.kodex_rang, VerfassungsKodexRang.ORDNUNGS_KODEX)
        self.assertEqual(norm.prozedur, VerfassungsKodexProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kodex_weight, 0.45)

    def test_kki_verfassungs_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_verfassungs_kodex(kodex_id="kodex-230-expansion")
        norm = next(n for n in kodex.normen if n.geltung is VerfassungsKodexGeltung.GRUNDLEGEND_KODIFIZIERT)

        self.assertEqual(norm.kodex_rang, VerfassungsKodexRang.SOUVERAENITAETS_KODEX)
        self.assertEqual(norm.prozedur, VerfassungsKodexProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_verfassungs_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_verfassungs_kodex(kodex_id="kodex-230-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-230-signal-stability-lane",))
        self.assertEqual(kodex.kodifiziert_norm_ids, ("kodex-230-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-230-signal-expansion-lane",))

    def test_kki_grundrechts_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_grundrechts_senat(senat_id="senat-229-stability")
        norm = next(n for n in senat.normen if n.geltung is SenatGeltung.GESPERRT)

        self.assertIsInstance(senat, GrundrechtsSenat)
        self.assertIsInstance(norm, SenatNorm)
        self.assertEqual(norm.senat_rang, SenatRang.SCHUTZ_SENAT)
        self.assertEqual(norm.prozedur, SenatProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.senat_tier, 1)

    def test_kki_grundrechts_senat_builds_beschlossen_ordnungs_norm(self) -> None:
        senat = build_grundrechts_senat(senat_id="senat-229-governance")
        norm = next(n for n in senat.normen if n.geltung is SenatGeltung.BESCHLOSSEN)

        self.assertEqual(norm.senat_rang, SenatRang.ORDNUNGS_SENAT)
        self.assertEqual(norm.prozedur, SenatProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.senat_weight, 0.45)

    def test_kki_grundrechts_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_grundrechts_senat(senat_id="senat-229-expansion")
        norm = next(n for n in senat.normen if n.geltung is SenatGeltung.GRUNDLEGEND_BESCHLOSSEN)

        self.assertEqual(norm.senat_rang, SenatRang.SOUVERAENITAETS_SENAT)
        self.assertEqual(norm.prozedur, SenatProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_grundrechts_senat_aggregates_senat_signal(self) -> None:
        senat = build_grundrechts_senat(senat_id="senat-229-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-229-signal-stability-lane",))
        self.assertEqual(senat.beschlossen_norm_ids, ("senat-229-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-229-signal-expansion-lane",))

    def test_kki_ewigkeits_norm_builds_gesperrt_schutz_eintrag(self) -> None:
        norm = build_ewigkeits_norm(norm_id="norm-228-stability")
        eintrag = next(e for e in norm.eintraege if e.geltung is EwigkeitsGeltung.GESPERRT)

        self.assertIsInstance(norm, EwigkeitsNorm)
        self.assertIsInstance(eintrag, EwigkeitsEintrag)
        self.assertEqual(eintrag.ewigkeits_typ, EwigkeitsTyp.SCHUTZ_EWIGKEIT)
        self.assertEqual(eintrag.prozedur, EwigkeitsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.ewigkeits_tier, 1)

    def test_kki_ewigkeits_norm_builds_verewigt_ordnungs_eintrag(self) -> None:
        norm = build_ewigkeits_norm(norm_id="norm-228-governance")
        eintrag = next(e for e in norm.eintraege if e.geltung is EwigkeitsGeltung.VEREWIGT)

        self.assertEqual(eintrag.ewigkeits_typ, EwigkeitsTyp.ORDNUNGS_EWIGKEIT)
        self.assertEqual(eintrag.prozedur, EwigkeitsProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.ewigkeits_weight, 0.45)

    def test_kki_ewigkeits_norm_builds_grundlegend_souveraenitaets_eintrag(self) -> None:
        norm = build_ewigkeits_norm(norm_id="norm-228-expansion")
        eintrag = next(e for e in norm.eintraege if e.geltung is EwigkeitsGeltung.GRUNDLEGEND_VEREWIGT)

        self.assertEqual(eintrag.ewigkeits_typ, EwigkeitsTyp.SOUVERAENITAETS_EWIGKEIT)
        self.assertEqual(eintrag.prozedur, EwigkeitsProzedur.PLENARPROTOKOLL)
        self.assertTrue(eintrag.canonical)

    def test_kki_ewigkeits_norm_aggregates_norm_signal(self) -> None:
        norm = build_ewigkeits_norm(norm_id="norm-228-signal")

        self.assertEqual(norm.norm_signal.status, "norm-gesperrt")
        self.assertEqual(norm.gesperrt_eintrag_ids, ("norm-228-signal-stability-lane",))
        self.assertEqual(norm.verewigt_eintrag_ids, ("norm-228-signal-governance-lane",))
        self.assertEqual(norm.grundlegend_eintrag_ids, ("norm-228-signal-expansion-lane",))

    def test_kki_supremats_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_supremats_register(register_id="register-227-stability")
        norm = next(n for n in register.normen if n.geltung is SuprematsGeltung.GESPERRT)

        self.assertIsInstance(register, SuprematsRegister)
        self.assertIsInstance(norm, SuprematsNorm)
        self.assertEqual(norm.supremats_klasse, SuprematsKlasse.SCHUTZ_SUPREMAT)
        self.assertEqual(norm.prozedur, SuprematsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.supremats_tier, 1)

    def test_kki_supremats_register_builds_supremiert_ordnungs_norm(self) -> None:
        register = build_supremats_register(register_id="register-227-governance")
        norm = next(n for n in register.normen if n.geltung is SuprematsGeltung.SUPREMIERT)

        self.assertEqual(norm.supremats_klasse, SuprematsKlasse.ORDNUNGS_SUPREMAT)
        self.assertEqual(norm.prozedur, SuprematsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.supremats_weight, 0.45)

    def test_kki_supremats_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_supremats_register(register_id="register-227-expansion")
        norm = next(n for n in register.normen if n.geltung is SuprematsGeltung.GRUNDLEGEND_SUPREMIERT)

        self.assertEqual(norm.supremats_klasse, SuprematsKlasse.SOUVERAENITAETS_SUPREMAT)
        self.assertEqual(norm.prozedur, SuprematsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_supremats_register_aggregates_register_signal(self) -> None:
        register = build_supremats_register(register_id="register-227-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-227-signal-stability-lane",))
        self.assertEqual(register.supremiert_norm_ids, ("register-227-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-227-signal-expansion-lane",))

    def test_kki_hoheits_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_hoheits_manifest(manifest_id="manifest-226-stability")
        norm = next(n for n in manifest.normen if n.geltung is HoheitsGeltung.GESPERRT)

        self.assertIsInstance(manifest, HoheitsManifest)
        self.assertIsInstance(norm, HoheitsNorm)
        self.assertEqual(norm.hoheits_grad, HoheitsGrad.SCHUTZ_GRAD)
        self.assertEqual(norm.prozedur, HoheitsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.hoheits_tier, 1)

    def test_kki_hoheits_manifest_builds_proklamiert_ordnungs_norm(self) -> None:
        manifest = build_hoheits_manifest(manifest_id="manifest-226-governance")
        norm = next(n for n in manifest.normen if n.geltung is HoheitsGeltung.PROKLAMIERT)

        self.assertEqual(norm.hoheits_grad, HoheitsGrad.ORDNUNGS_GRAD)
        self.assertEqual(norm.prozedur, HoheitsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.hoheits_weight, 0.45)

    def test_kki_hoheits_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_hoheits_manifest(manifest_id="manifest-226-expansion")
        norm = next(n for n in manifest.normen if n.geltung is HoheitsGeltung.GRUNDLEGEND_PROKLAMIERT)

        self.assertEqual(norm.hoheits_grad, HoheitsGrad.SOUVERAENITAETS_GRAD)
        self.assertEqual(norm.prozedur, HoheitsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_hoheits_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_hoheits_manifest(manifest_id="manifest-226-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-226-signal-stability-lane",))
        self.assertEqual(manifest.proklamiert_norm_ids, ("manifest-226-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-226-signal-expansion-lane",))

    def test_kki_bundes_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_bundes_charta(charta_id="charta-225-stability")
        norm = next(n for n in charta.normen if n.geltung is BundesGeltung.GESPERRT)

        self.assertIsInstance(charta, BundesCharta)
        self.assertIsInstance(norm, BundesNorm)
        self.assertEqual(norm.bundes_rang, BundesRang.SCHUTZ_RANG)
        self.assertEqual(norm.prozedur, BundesProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.bundes_tier, 1)

    def test_kki_bundes_charta_builds_verbuergt_ordnungs_norm(self) -> None:
        charta = build_bundes_charta(charta_id="charta-225-governance")
        norm = next(n for n in charta.normen if n.geltung is BundesGeltung.VERBUERGT)

        self.assertEqual(norm.bundes_rang, BundesRang.ORDNUNGS_RANG)
        self.assertEqual(norm.prozedur, BundesProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.bundes_weight, 0.45)

    def test_kki_bundes_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_bundes_charta(charta_id="charta-225-expansion")
        norm = next(n for n in charta.normen if n.geltung is BundesGeltung.GRUNDLEGEND_VERBUERGT)

        self.assertEqual(norm.bundes_rang, BundesRang.SOUVERAENITAETS_RANG)
        self.assertEqual(norm.prozedur, BundesProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_bundes_charta_aggregates_charta_signal(self) -> None:
        charta = build_bundes_charta(charta_id="charta-225-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-225-signal-stability-lane",))
        self.assertEqual(charta.verbuergt_norm_ids, ("charta-225-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-225-signal-expansion-lane",))

    def test_kki_foederal_vertrag_builds_gesperrt_schutz_norm(self) -> None:
        vertrag = build_foederal_vertrag(vertrag_id="vertrag-224-stability")
        norm = next(n for n in vertrag.normen if n.geltung is FoederalGeltung.GESPERRT)

        self.assertIsInstance(vertrag, FoederalVertrag)
        self.assertIsInstance(norm, FoederalNorm)
        self.assertEqual(norm.foederal_typ, FoederalTyp.SCHUTZ_BUND)
        self.assertEqual(norm.prozedur, FoederalProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.foederal_tier, 1)

    def test_kki_foederal_vertrag_builds_foederiert_ordnungs_norm(self) -> None:
        vertrag = build_foederal_vertrag(vertrag_id="vertrag-224-governance")
        norm = next(n for n in vertrag.normen if n.geltung is FoederalGeltung.FOEDERIERT)

        self.assertEqual(norm.foederal_typ, FoederalTyp.ORDNUNGS_BUND)
        self.assertEqual(norm.prozedur, FoederalProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.foederal_weight, 0.45)

    def test_kki_foederal_vertrag_builds_grundlegend_souveraenitaets_norm(self) -> None:
        vertrag = build_foederal_vertrag(vertrag_id="vertrag-224-expansion")
        norm = next(n for n in vertrag.normen if n.geltung is FoederalGeltung.GRUNDLEGEND_FOEDERIERT)

        self.assertEqual(norm.foederal_typ, FoederalTyp.SOUVERAENITAETS_BUND)
        self.assertEqual(norm.prozedur, FoederalProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_foederal_vertrag_aggregates_vertrag_signal(self) -> None:
        vertrag = build_foederal_vertrag(vertrag_id="vertrag-224-signal")

        self.assertEqual(vertrag.vertrag_signal.status, "vertrag-gesperrt")
        self.assertEqual(vertrag.gesperrt_norm_ids, ("vertrag-224-signal-stability-lane",))
        self.assertEqual(vertrag.foederiert_norm_ids, ("vertrag-224-signal-governance-lane",))
        self.assertEqual(vertrag.grundlegend_norm_ids, ("vertrag-224-signal-expansion-lane",))

    def test_kki_unions_akt_builds_gesperrt_schutz_norm(self) -> None:
        akt = build_unions_akt(akt_id="akt-223-stability")
        norm = next(n for n in akt.normen if n.geltung is UnionsGeltung.GESPERRT)

        self.assertIsInstance(akt, UnionsAkt)
        self.assertIsInstance(norm, UnionsNorm)
        self.assertEqual(norm.unions_typ, UnionsTyp.SCHUTZ_UNION)
        self.assertEqual(norm.prozedur, UnionsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.unions_tier, 1)

    def test_kki_unions_akt_builds_vereint_ordnungs_norm(self) -> None:
        akt = build_unions_akt(akt_id="akt-223-governance")
        norm = next(n for n in akt.normen if n.geltung is UnionsGeltung.VEREINT)

        self.assertEqual(norm.unions_typ, UnionsTyp.ORDNUNGS_UNION)
        self.assertEqual(norm.prozedur, UnionsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.unions_weight, 0.45)

    def test_kki_unions_akt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        akt = build_unions_akt(akt_id="akt-223-expansion")
        norm = next(n for n in akt.normen if n.geltung is UnionsGeltung.GRUNDLEGEND_VEREINT)

        self.assertEqual(norm.unions_typ, UnionsTyp.SOUVERAENITAETS_UNION)
        self.assertEqual(norm.prozedur, UnionsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_unions_akt_aggregates_akt_signal(self) -> None:
        akt = build_unions_akt(akt_id="akt-223-signal")

        self.assertEqual(akt.akt_signal.status, "akt-gesperrt")
        self.assertEqual(akt.gesperrt_norm_ids, ("akt-223-signal-stability-lane",))
        self.assertEqual(akt.vereint_norm_ids, ("akt-223-signal-governance-lane",))
        self.assertEqual(akt.grundlegend_norm_ids, ("akt-223-signal-expansion-lane",))

    def test_kki_rechts_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_rechts_kodex(kodex_id="kodex-222-stability")
        norm = next(n for n in kodex.normen if n.status is KodexStatus.GESPERRT)

        self.assertIsInstance(kodex, RechtsKodex)
        self.assertIsInstance(norm, KodexNorm)
        self.assertEqual(norm.klasse, KodexKlasse.SCHUTZ_KLASSE)
        self.assertEqual(norm.prozedur, KodexProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kodex_tier, 1)

    def test_kki_rechts_kodex_builds_kodiert_ordnungs_norm(self) -> None:
        kodex = build_rechts_kodex(kodex_id="kodex-222-governance")
        norm = next(n for n in kodex.normen if n.status is KodexStatus.KODIERT)

        self.assertEqual(norm.klasse, KodexKlasse.ORDNUNGS_KLASSE)
        self.assertEqual(norm.prozedur, KodexProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kodex_weight, 0.45)

    def test_kki_rechts_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_rechts_kodex(kodex_id="kodex-222-expansion")
        norm = next(n for n in kodex.normen if n.status is KodexStatus.GRUNDLEGEND_KODIERT)

        self.assertEqual(norm.klasse, KodexKlasse.SOUVERAENITAETS_KLASSE)
        self.assertEqual(norm.prozedur, KodexProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_rechts_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_rechts_kodex(kodex_id="kodex-222-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-222-signal-stability-lane",))
        self.assertEqual(kodex.kodiert_norm_ids, ("kodex-222-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-222-signal-expansion-lane",))

    def test_kki_staats_ordnung_builds_gesperrt_schutz_norm(self) -> None:
        ordnung = build_staats_ordnung(ordnung_id="ordnung-221-stability")
        norm = next(n for n in ordnung.normen if n.geltung is StaatsGeltung.GESPERRT)

        self.assertIsInstance(ordnung, StaatsOrdnung)
        self.assertIsInstance(norm, StaatsNorm)
        self.assertEqual(norm.ebene, StaatsEbene.SCHUTZ_EBENE)
        self.assertEqual(norm.prozedur, StaatsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.staats_tier, 1)

    def test_kki_staats_ordnung_builds_geordnet_ordnungs_norm(self) -> None:
        ordnung = build_staats_ordnung(ordnung_id="ordnung-221-governance")
        norm = next(n for n in ordnung.normen if n.geltung is StaatsGeltung.GEORDNET)

        self.assertEqual(norm.ebene, StaatsEbene.ORDNUNGS_EBENE)
        self.assertEqual(norm.prozedur, StaatsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.staats_weight, 0.45)

    def test_kki_staats_ordnung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        ordnung = build_staats_ordnung(ordnung_id="ordnung-221-expansion")
        norm = next(n for n in ordnung.normen if n.geltung is StaatsGeltung.GRUNDLEGEND_GEORDNET)

        self.assertEqual(norm.ebene, StaatsEbene.SOUVERAENITAETS_EBENE)
        self.assertEqual(norm.prozedur, StaatsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_staats_ordnung_aggregates_staats_signal(self) -> None:
        ordnung = build_staats_ordnung(ordnung_id="ordnung-221-signal")

        self.assertEqual(ordnung.staats_signal.status, "ordnung-gesperrt")
        self.assertEqual(ordnung.gesperrt_norm_ids, ("ordnung-221-signal-stability-lane",))
        self.assertEqual(ordnung.geordnet_norm_ids, ("ordnung-221-signal-governance-lane",))
        self.assertEqual(ordnung.grundlegend_norm_ids, ("ordnung-221-signal-expansion-lane",))

    def test_kki_verfassungs_grundgesetz_builds_gesperrt_schutz_paragraph(self) -> None:
        grundgesetz = build_verfassungs_grundgesetz(grundgesetz_id="grundgesetz-220-stability")
        paragraph = next(p for p in grundgesetz.paragraphen if p.geltung is GrundgesetzGeltung.GESPERRT)

        self.assertIsInstance(grundgesetz, VerfassungsGrundgesetz)
        self.assertIsInstance(paragraph, GrundgesetzParagraph)
        self.assertEqual(paragraph.titel, GrundgesetzTitel.SCHUTZ_TITEL)
        self.assertEqual(paragraph.prozedur, GrundgesetzProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(paragraph.grundgesetz_tier, 1)

    def test_kki_verfassungs_grundgesetz_builds_verbindlich_ordnungs_paragraph(self) -> None:
        grundgesetz = build_verfassungs_grundgesetz(grundgesetz_id="grundgesetz-220-governance")
        paragraph = next(p for p in grundgesetz.paragraphen if p.geltung is GrundgesetzGeltung.VERBINDLICH)

        self.assertEqual(paragraph.titel, GrundgesetzTitel.ORDNUNGS_TITEL)
        self.assertEqual(paragraph.prozedur, GrundgesetzProzedur.REGELPROTOKOLL)
        self.assertGreater(paragraph.grundgesetz_weight, 0.45)

    def test_kki_verfassungs_grundgesetz_builds_grundgesetzlich_souveraenitaets_paragraph(self) -> None:
        grundgesetz = build_verfassungs_grundgesetz(grundgesetz_id="grundgesetz-220-expansion")
        paragraph = next(p for p in grundgesetz.paragraphen if p.geltung is GrundgesetzGeltung.GRUNDGESETZLICH)

        self.assertEqual(paragraph.titel, GrundgesetzTitel.SOUVERAENITAETS_TITEL)
        self.assertEqual(paragraph.prozedur, GrundgesetzProzedur.PLENARPROTOKOLL)
        self.assertTrue(paragraph.canonical)

    def test_kki_verfassungs_grundgesetz_aggregates_grundgesetz_signal(self) -> None:
        grundgesetz = build_verfassungs_grundgesetz(grundgesetz_id="grundgesetz-220-signal")

        self.assertEqual(grundgesetz.grundgesetz_signal.status, "grundgesetz-gesperrt")
        self.assertEqual(grundgesetz.gesperrt_paragraph_ids, ("grundgesetz-220-signal-stability-lane",))
        self.assertEqual(grundgesetz.verbindlich_paragraph_ids, ("grundgesetz-220-signal-governance-lane",))
        self.assertEqual(grundgesetz.grundgesetzlich_paragraph_ids, ("grundgesetz-220-signal-expansion-lane",))

    def test_kki_leitstern_konstitution_builds_gesperrt_schutz_artikel(self) -> None:
        konstitution = build_leitstern_konstitution(konstitutions_id="konstitution-219-stability")
        artikel = next(a for a in konstitution.artikel if a.rang is KonstitutionsRang.GESPERRT)

        self.assertIsInstance(konstitution, LeitsternKonstitution)
        self.assertIsInstance(artikel, KonstitutionsArtikel)
        self.assertEqual(artikel.ebene, KonstitutionsEbene.SCHUTZ_EBENE)
        self.assertEqual(artikel.prozedur, KonstitutionsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(artikel.konstitutions_tier, 1)

    def test_kki_leitstern_konstitution_builds_konstituiert_ordnungs_artikel(self) -> None:
        konstitution = build_leitstern_konstitution(konstitutions_id="konstitution-219-governance")
        artikel = next(a for a in konstitution.artikel if a.rang is KonstitutionsRang.KONSTITUIERT)

        self.assertEqual(artikel.ebene, KonstitutionsEbene.ORDNUNGS_EBENE)
        self.assertEqual(artikel.prozedur, KonstitutionsProzedur.REGELPROTOKOLL)
        self.assertGreater(artikel.konstitutions_weight, 0.45)

    def test_kki_leitstern_konstitution_builds_grundlegend_souveraenitaets_artikel(self) -> None:
        konstitution = build_leitstern_konstitution(konstitutions_id="konstitution-219-expansion")
        artikel = next(a for a in konstitution.artikel if a.rang is KonstitutionsRang.GRUNDLEGEND_KONSTITUIERT)

        self.assertEqual(artikel.ebene, KonstitutionsEbene.SOUVERAENITAETS_EBENE)
        self.assertEqual(artikel.prozedur, KonstitutionsProzedur.PLENARPROTOKOLL)
        self.assertTrue(artikel.canonical)

    def test_kki_leitstern_konstitution_aggregates_konstitutions_signal(self) -> None:
        konstitution = build_leitstern_konstitution(konstitutions_id="konstitution-219-signal")

        self.assertEqual(konstitution.konstitutions_signal.status, "konstitution-gesperrt")
        self.assertEqual(konstitution.gesperrt_artikel_ids, ("konstitution-219-signal-stability-lane",))
        self.assertEqual(konstitution.konstituiert_artikel_ids, ("konstitution-219-signal-governance-lane",))
        self.assertEqual(konstitution.grundlegend_artikel_ids, ("konstitution-219-signal-expansion-lane",))

    def test_kki_zweck_manifest_builds_gesperrt_schutz_klausel(self) -> None:
        manifest = build_zweck_manifest(manifest_id="manifest-218-stability")
        klausel = next(k for k in manifest.klauseln if k.geltung is ManifestGeltung.GESPERRT)

        self.assertIsInstance(manifest, ZweckManifest)
        self.assertIsInstance(klausel, ZweckKlausel)
        self.assertEqual(klausel.dimension, ZweckDimension.SCHUTZ_DIMENSION)
        self.assertEqual(klausel.prozedur, ManifestProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(klausel.manifest_tier, 1)

    def test_kki_zweck_manifest_builds_proklamiert_ordnungs_klausel(self) -> None:
        manifest = build_zweck_manifest(manifest_id="manifest-218-governance")
        klausel = next(k for k in manifest.klauseln if k.geltung is ManifestGeltung.PROKLAMIERT)

        self.assertEqual(klausel.dimension, ZweckDimension.ORDNUNGS_DIMENSION)
        self.assertEqual(klausel.prozedur, ManifestProzedur.REGELPROTOKOLL)
        self.assertGreater(klausel.manifest_weight, 0.45)

    def test_kki_zweck_manifest_builds_grundlegend_souveraenitaets_klausel(self) -> None:
        manifest = build_zweck_manifest(manifest_id="manifest-218-expansion")
        klausel = next(k for k in manifest.klauseln if k.geltung is ManifestGeltung.GRUNDLEGEND_PROKLAMIERT)

        self.assertEqual(klausel.dimension, ZweckDimension.SOUVERAENITAETS_DIMENSION)
        self.assertEqual(klausel.prozedur, ManifestProzedur.PLENARPROTOKOLL)
        self.assertTrue(klausel.canonical)

    def test_kki_zweck_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_zweck_manifest(manifest_id="manifest-218-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_klausel_ids, ("manifest-218-signal-stability-lane",))
        self.assertEqual(manifest.proklamiert_klausel_ids, ("manifest-218-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_klausel_ids, ("manifest-218-signal-expansion-lane",))

    def test_kki_missions_verfassung_builds_gesperrt_schutz_artikel(self) -> None:
        verfassung = build_missions_verfassung(verfassungs_id="verfassung-217-stability")
        artikel = next(a for a in verfassung.artikel if a.status is VerfassungsStatus.GESPERRT)

        self.assertIsInstance(verfassung, MissionsVerfassung)
        self.assertIsInstance(artikel, MissionsArtikel)
        self.assertEqual(artikel.rang, MissionsRang.SCHUTZ_RANG)
        self.assertEqual(artikel.prozedur, VerfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(artikel.verfassungs_tier, 1)

    def test_kki_missions_verfassung_builds_ratifiziert_ordnungs_artikel(self) -> None:
        verfassung = build_missions_verfassung(verfassungs_id="verfassung-217-governance")
        artikel = next(a for a in verfassung.artikel if a.status is VerfassungsStatus.RATIFIZIERT)

        self.assertEqual(artikel.rang, MissionsRang.ORDNUNGS_RANG)
        self.assertEqual(artikel.prozedur, VerfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(artikel.verfassungs_weight, 0.45)

    def test_kki_missions_verfassung_builds_grundlegend_souveraenitaets_artikel(self) -> None:
        verfassung = build_missions_verfassung(verfassungs_id="verfassung-217-expansion")
        artikel = next(a for a in verfassung.artikel if a.status is VerfassungsStatus.GRUNDLEGEND_RATIFIZIERT)

        self.assertEqual(artikel.rang, MissionsRang.SOUVERAENITAETS_RANG)
        self.assertEqual(artikel.prozedur, VerfassungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(artikel.canonical)

    def test_kki_missions_verfassung_aggregates_verfassungs_signal(self) -> None:
        verfassung = build_missions_verfassung(verfassungs_id="verfassung-217-signal")

        self.assertEqual(verfassung.verfassungs_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_artikel_ids, ("verfassung-217-signal-stability-lane",))
        self.assertEqual(verfassung.ratifiziert_artikel_ids, ("verfassung-217-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_artikel_ids, ("verfassung-217-signal-expansion-lane",))

    def test_kki_leitbild_konvent_builds_gesperrt_schutz_resolution(self) -> None:
        konvent = build_leitbild_konvent(konvent_id="konvent-216-stability")
        resolution = next(r for r in konvent.resolutionen if r.beschluss is KonventBeschluss.GESPERRT)

        self.assertIsInstance(konvent, LeitbildKonvent)
        self.assertIsInstance(resolution, LeitbildResolution)
        self.assertEqual(resolution.ausrichtung, LeitbildAusrichtung.SCHUTZ_AUSRICHTUNG)
        self.assertEqual(resolution.prozedur, KonventProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(resolution.konvent_tier, 1)

    def test_kki_leitbild_konvent_builds_beschlossen_ordnungs_resolution(self) -> None:
        konvent = build_leitbild_konvent(konvent_id="konvent-216-governance")
        resolution = next(r for r in konvent.resolutionen if r.beschluss is KonventBeschluss.BESCHLOSSEN)

        self.assertEqual(resolution.ausrichtung, LeitbildAusrichtung.ORDNUNGS_AUSRICHTUNG)
        self.assertEqual(resolution.prozedur, KonventProzedur.REGELPROTOKOLL)
        self.assertGreater(resolution.konvent_weight, 0.45)

    def test_kki_leitbild_konvent_builds_grundlegend_souveraenitaets_resolution(self) -> None:
        konvent = build_leitbild_konvent(konvent_id="konvent-216-expansion")
        resolution = next(r for r in konvent.resolutionen if r.beschluss is KonventBeschluss.GRUNDLEGEND_BESCHLOSSEN)

        self.assertEqual(resolution.ausrichtung, LeitbildAusrichtung.SOUVERAENITAETS_AUSRICHTUNG)
        self.assertEqual(resolution.prozedur, KonventProzedur.PLENARPROTOKOLL)
        self.assertTrue(resolution.canonical)

    def test_kki_leitbild_konvent_aggregates_konvent_signal(self) -> None:
        konvent = build_leitbild_konvent(konvent_id="konvent-216-signal")

        self.assertEqual(konvent.konvent_signal.status, "konvent-gesperrt")
        self.assertEqual(konvent.gesperrt_resolution_ids, ("konvent-216-signal-stability-lane",))
        self.assertEqual(konvent.beschlossen_resolution_ids, ("konvent-216-signal-governance-lane",))
        self.assertEqual(konvent.grundlegend_resolution_ids, ("konvent-216-signal-expansion-lane",))

    def test_kki_werte_charta_builds_gesperrt_schutz_artikel(self) -> None:
        charta = build_werte_charta(charta_id="charta-215-stability")
        artikel = next(a for a in charta.artikel if a.status is WerteStatus.GESPERRT)

        self.assertIsInstance(charta, WerteCharta)
        self.assertIsInstance(artikel, WerteArtikel)
        self.assertEqual(artikel.typ, WerteTyp.SCHUTZ_WERT)
        self.assertEqual(artikel.prozedur, WerteProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(artikel.charta_tier, 1)

    def test_kki_werte_charta_builds_verankert_ordnungs_artikel(self) -> None:
        charta = build_werte_charta(charta_id="charta-215-governance")
        artikel = next(a for a in charta.artikel if a.status is WerteStatus.VERANKERT)

        self.assertEqual(artikel.typ, WerteTyp.ORDNUNGS_WERT)
        self.assertEqual(artikel.prozedur, WerteProzedur.REGELPROTOKOLL)
        self.assertGreater(artikel.charta_weight, 0.45)

    def test_kki_werte_charta_builds_grundlegend_souveraenitaets_artikel(self) -> None:
        charta = build_werte_charta(charta_id="charta-215-expansion")
        artikel = next(a for a in charta.artikel if a.status is WerteStatus.GRUNDLEGEND_VERANKERT)

        self.assertEqual(artikel.typ, WerteTyp.SOUVERAENITAETS_WERT)
        self.assertEqual(artikel.prozedur, WerteProzedur.PLENARPROTOKOLL)
        self.assertTrue(artikel.canonical)

    def test_kki_werte_charta_aggregates_charta_signal(self) -> None:
        charta = build_werte_charta(charta_id="charta-215-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_artikel_ids, ("charta-215-signal-stability-lane",))
        self.assertEqual(charta.verankert_artikel_ids, ("charta-215-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_artikel_ids, ("charta-215-signal-expansion-lane",))

    def test_kki_prinzipien_kodex_builds_gesperrt_schutz_satz(self) -> None:
        kodex = build_prinzipien_kodex(kodex_id="kodex-214-stability")
        satz = next(s for s in kodex.saetze if s.status is PrinzipienStatus.GESPERRT)

        self.assertIsInstance(kodex, PrinzipienKodex)
        self.assertIsInstance(satz, PrinzipienSatz)
        self.assertEqual(satz.klasse, PrinzipienKlasse.SCHUTZ_KLASSE)
        self.assertEqual(satz.prozedur, PrinzipienProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(satz.kodex_tier, 1)

    def test_kki_prinzipien_kodex_builds_kodifiziert_ordnungs_satz(self) -> None:
        kodex = build_prinzipien_kodex(kodex_id="kodex-214-governance")
        satz = next(s for s in kodex.saetze if s.status is PrinzipienStatus.KODIFIZIERT)

        self.assertEqual(satz.klasse, PrinzipienKlasse.ORDNUNGS_KLASSE)
        self.assertEqual(satz.prozedur, PrinzipienProzedur.REGELPROTOKOLL)
        self.assertGreater(satz.kodex_weight, 0.45)

    def test_kki_prinzipien_kodex_builds_grundlegend_souveraenitaets_satz(self) -> None:
        kodex = build_prinzipien_kodex(kodex_id="kodex-214-expansion")
        satz = next(s for s in kodex.saetze if s.status is PrinzipienStatus.GRUNDLEGEND_KODIFIZIERT)

        self.assertEqual(satz.klasse, PrinzipienKlasse.SOUVERAENITAETS_KLASSE)
        self.assertEqual(satz.prozedur, PrinzipienProzedur.PLENARPROTOKOLL)
        self.assertTrue(satz.canonical)

    def test_kki_prinzipien_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_prinzipien_kodex(kodex_id="kodex-214-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_satz_ids, ("kodex-214-signal-stability-lane",))
        self.assertEqual(kodex.kodifiziert_satz_ids, ("kodex-214-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_satz_ids, ("kodex-214-signal-expansion-lane",))

    def test_kki_grundsatz_register_builds_gesperrt_schutz_eintrag(self) -> None:
        register = build_grundsatz_register(register_id="register-213-stability")
        eintrag = next(e for e in register.eintraege if e.status is RegisterStatus.GESPERRT)

        self.assertIsInstance(register, GrundsatzRegister)
        self.assertIsInstance(eintrag, RegisterEintrag)
        self.assertEqual(eintrag.kategorie, RegisterKategorie.SCHUTZ_KATEGORIE)
        self.assertEqual(eintrag.prozedur, RegisterProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.registry_tier, 1)

    def test_kki_grundsatz_register_builds_eingetragen_ordnungs_eintrag(self) -> None:
        register = build_grundsatz_register(register_id="register-213-governance")
        eintrag = next(e for e in register.eintraege if e.status is RegisterStatus.EINGETRAGEN)

        self.assertEqual(eintrag.kategorie, RegisterKategorie.ORDNUNGS_KATEGORIE)
        self.assertEqual(eintrag.prozedur, RegisterProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.register_weight, 0.45)

    def test_kki_grundsatz_register_builds_grundlegend_souveraenitaets_eintrag(self) -> None:
        register = build_grundsatz_register(register_id="register-213-expansion")
        eintrag = next(e for e in register.eintraege if e.status is RegisterStatus.GRUNDLEGEND_EINGETRAGEN)

        self.assertEqual(eintrag.kategorie, RegisterKategorie.SOUVERAENITAETS_KATEGORIE)
        self.assertEqual(eintrag.prozedur, RegisterProzedur.PLENARPROTOKOLL)
        self.assertTrue(eintrag.canonical)

    def test_kki_grundsatz_register_aggregates_register_signal(self) -> None:
        register = build_grundsatz_register(register_id="register-213-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_eintrag_ids, ("register-213-signal-stability-lane",))
        self.assertEqual(register.eingetragen_eintrag_ids, ("register-213-signal-governance-lane",))
        self.assertEqual(register.grundlegend_eintrag_ids, ("register-213-signal-expansion-lane",))

    def test_kki_rechts_fundament_builds_gesperrt_schutz_pfeiler(self) -> None:
        fundament = build_rechts_fundament(fundament_id="fundament-212-stability")
        pfeiler = next(p for p in fundament.pfeiler if p.kraft is FundamentKraft.GESPERRT)

        self.assertIsInstance(fundament, RechtsFundament)
        self.assertIsInstance(pfeiler, FundamentPfeiler)
        self.assertEqual(pfeiler.saeule, FundamentSaeule.SCHUTZ_SAEULE)
        self.assertEqual(pfeiler.verfahren, FundamentVerfahren.NOTVERFAHREN)
        self.assertGreaterEqual(pfeiler.foundation_depth, 1)

    def test_kki_rechts_fundament_builds_fundiert_ordnungs_pfeiler(self) -> None:
        fundament = build_rechts_fundament(fundament_id="fundament-212-governance")
        pfeiler = next(p for p in fundament.pfeiler if p.kraft is FundamentKraft.FUNDIERT)

        self.assertEqual(pfeiler.saeule, FundamentSaeule.ORDNUNGS_SAEULE)
        self.assertEqual(pfeiler.verfahren, FundamentVerfahren.REGELVERFAHREN)
        self.assertGreater(pfeiler.fundament_weight, 0.45)

    def test_kki_rechts_fundament_builds_tragendes_recht_souveraenitaets_pfeiler(self) -> None:
        fundament = build_rechts_fundament(fundament_id="fundament-212-expansion")
        pfeiler = next(p for p in fundament.pfeiler if p.kraft is FundamentKraft.TRAGENDES_RECHT)

        self.assertEqual(pfeiler.saeule, FundamentSaeule.SOUVERAENITAETS_SAEULE)
        self.assertEqual(pfeiler.verfahren, FundamentVerfahren.PLENARVERFAHREN)
        self.assertTrue(pfeiler.load_bearing)

    def test_kki_rechts_fundament_aggregates_fundament_signal(self) -> None:
        fundament = build_rechts_fundament(fundament_id="fundament-212-signal")

        self.assertEqual(fundament.fundament_signal.status, "fundament-gesperrt")
        self.assertEqual(fundament.gesperrt_pfeiler_ids, ("fundament-212-signal-stability-lane",))
        self.assertEqual(fundament.fundiert_pfeiler_ids, ("fundament-212-signal-governance-lane",))
        self.assertEqual(fundament.tragendes_recht_pfeiler_ids, ("fundament-212-signal-expansion-lane",))

    def test_kki_autoritaets_dekret_builds_gesperrt_schutz_klausel(self) -> None:
        dekret = build_autoritaets_dekret(dekret_id="dekret-211-stability")
        klausel = next(k for k in dekret.klauseln if k.geltung is DekretGeltung.GESPERRT)

        self.assertIsInstance(dekret, AutoritaetsDekret)
        self.assertIsInstance(klausel, DekretKlausel)
        self.assertEqual(klausel.sektion, DekretSektion.SCHUTZ_SEKTION)
        self.assertEqual(klausel.prozedur, DekretProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(klausel.decree_order, 1)

    def test_kki_autoritaets_dekret_builds_verordnet_ordnungs_klausel(self) -> None:
        dekret = build_autoritaets_dekret(dekret_id="dekret-211-governance")
        klausel = next(k for k in dekret.klauseln if k.geltung is DekretGeltung.VERORDNET)

        self.assertEqual(klausel.sektion, DekretSektion.ORDNUNGS_SEKTION)
        self.assertEqual(klausel.prozedur, DekretProzedur.REGELPROZEDUR)
        self.assertGreater(klausel.dekret_weight, 0.45)

    def test_kki_autoritaets_dekret_builds_autoritaetsrecht_souveraenitaets_klausel(self) -> None:
        dekret = build_autoritaets_dekret(dekret_id="dekret-211-expansion")
        klausel = next(k for k in dekret.klauseln if k.geltung is DekretGeltung.AUTORITAETSRECHT)

        self.assertEqual(klausel.sektion, DekretSektion.SOUVERAENITAETS_SEKTION)
        self.assertEqual(klausel.prozedur, DekretProzedur.PLENARPROZEDUR)
        self.assertTrue(klausel.decreed)

    def test_kki_autoritaets_dekret_aggregates_dekret_signal(self) -> None:
        dekret = build_autoritaets_dekret(dekret_id="dekret-211-signal")

        self.assertEqual(dekret.dekret_signal.status, "dekret-gesperrt")
        self.assertEqual(dekret.gesperrt_klausel_ids, ("dekret-211-signal-stability-lane",))
        self.assertEqual(dekret.verordnet_klausel_ids, ("dekret-211-signal-governance-lane",))
        self.assertEqual(dekret.autoritaetsrecht_klausel_ids, ("dekret-211-signal-expansion-lane",))

    def test_kki_leitordnung_builds_blockiert_schutz_norm(self) -> None:
        ordnung = build_leitordnung(ordnung_id="ordnung-210-stability")
        norm = next(n for n in ordnung.normen if n.kraft is OrdnungsKraft.BLOCKIERT)

        self.assertIsInstance(ordnung, Leitordnung)
        self.assertIsInstance(norm, OrdnungsNorm)
        self.assertEqual(norm.rang, OrdnungsRang.SCHUTZ_RANG)
        self.assertEqual(norm.typ, OrdnungsTyp.NOTORDNUNG)
        self.assertGreaterEqual(norm.authority_level, 1)

    def test_kki_leitordnung_builds_wirksam_ordnungs_norm(self) -> None:
        ordnung = build_leitordnung(ordnung_id="ordnung-210-governance")
        norm = next(n for n in ordnung.normen if n.kraft is OrdnungsKraft.WIRKSAM)

        self.assertEqual(norm.rang, OrdnungsRang.ORDNUNGS_RANG)
        self.assertEqual(norm.typ, OrdnungsTyp.REGELORDNUNG)
        self.assertGreater(norm.ordnungs_weight, 0.45)

    def test_kki_leitordnung_builds_leitend_souveraenitaets_norm(self) -> None:
        ordnung = build_leitordnung(ordnung_id="ordnung-210-expansion")
        norm = next(n for n in ordnung.normen if n.kraft is OrdnungsKraft.LEITEND)

        self.assertEqual(norm.rang, OrdnungsRang.SOUVERAENITAETS_RANG)
        self.assertEqual(norm.typ, OrdnungsTyp.PLENARORDNUNG)
        self.assertTrue(norm.supreme)

    def test_kki_leitordnung_aggregates_ordnungs_signal(self) -> None:
        ordnung = build_leitordnung(ordnung_id="ordnung-210-signal")

        self.assertEqual(ordnung.ordnungs_signal.status, "ordnung-blockiert")
        self.assertEqual(ordnung.blockiert_norm_ids, ("ordnung-210-signal-stability-lane",))
        self.assertEqual(ordnung.wirksam_norm_ids, ("ordnung-210-signal-governance-lane",))
        self.assertEqual(ordnung.leitend_norm_ids, ("ordnung-210-signal-expansion-lane",))

    def test_kki_ordnungs_manifest_builds_gesperrt_schutz_abschnitt(self) -> None:
        manifest = build_ordnungs_manifest(manifest_id="manifest-209-stability")
        abschnitt = next(a for a in manifest.abschnitte if a.geltung is ManifestGeltung.GESPERRT)

        self.assertIsInstance(manifest, OrdnungsManifest)
        self.assertIsInstance(abschnitt, ManifestAbschnitt)
        self.assertEqual(abschnitt.kapitel, ManifestKapitel.SCHUTZ_KAPITEL)
        self.assertEqual(abschnitt.verfahren, ManifestVerfahren.NOTVERFAHREN)
        self.assertGreaterEqual(abschnitt.proclamation_rank, 1)

    def test_kki_ordnungs_manifest_builds_proklamiert_ordnungs_abschnitt(self) -> None:
        manifest = build_ordnungs_manifest(manifest_id="manifest-209-governance")
        abschnitt = next(a for a in manifest.abschnitte if a.geltung is ManifestGeltung.PROKLAMIERT)

        self.assertEqual(abschnitt.kapitel, ManifestKapitel.ORDNUNGS_KAPITEL)
        self.assertEqual(abschnitt.verfahren, ManifestVerfahren.REGELVERFAHREN)
        self.assertGreater(abschnitt.manifest_weight, 0.45)

    def test_kki_ordnungs_manifest_builds_hoheitsrecht_souveraenitaets_abschnitt(self) -> None:
        manifest = build_ordnungs_manifest(manifest_id="manifest-209-expansion")
        abschnitt = next(a for a in manifest.abschnitte if a.geltung is ManifestGeltung.HOHEITSRECHT)

        self.assertEqual(abschnitt.kapitel, ManifestKapitel.SOUVERAENITAETS_KAPITEL)
        self.assertEqual(abschnitt.verfahren, ManifestVerfahren.PLENARVERFAHREN)
        self.assertTrue(abschnitt.promulgated)

    def test_kki_ordnungs_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_ordnungs_manifest(manifest_id="manifest-209-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_abschnitt_ids, ("manifest-209-signal-stability-lane",))
        self.assertEqual(manifest.proklamiert_abschnitt_ids, ("manifest-209-signal-governance-lane",))
        self.assertEqual(manifest.hoheitsrecht_abschnitt_ids, ("manifest-209-signal-expansion-lane",))

    def test_kki_souveraenitaets_akt_builds_suspendiert_schutz_klausel(self) -> None:
        akt = build_souveraenitaets_akt(akt_id="akt-208-stability")
        klausel = next(k for k in akt.klauseln if k.akt_status is AktStatus.SUSPENDIERT)

        self.assertIsInstance(akt, SouveraenitaetsAkt)
        self.assertIsInstance(klausel, AktKlausel)
        self.assertEqual(klausel.sektion, AktSektion.SCHUTZ_SEKTION)
        self.assertEqual(klausel.prozedur, AktProzedur.EILVERFAHREN)
        self.assertGreaterEqual(klausel.enactment_tier, 1)

    def test_kki_souveraenitaets_akt_builds_ratifiziert_ordnungs_klausel(self) -> None:
        akt = build_souveraenitaets_akt(akt_id="akt-208-governance")
        klausel = next(k for k in akt.klauseln if k.akt_status is AktStatus.RATIFIZIERT)

        self.assertEqual(klausel.sektion, AktSektion.ORDNUNGS_SEKTION)
        self.assertEqual(klausel.prozedur, AktProzedur.STANDARDVERFAHREN)
        self.assertGreater(klausel.sovereignty_weight, 0.45)

    def test_kki_souveraenitaets_akt_builds_souveraen_souveraenitaets_klausel(self) -> None:
        akt = build_souveraenitaets_akt(akt_id="akt-208-expansion")
        klausel = next(k for k in akt.klauseln if k.akt_status is AktStatus.SOUVERAEN)

        self.assertEqual(klausel.sektion, AktSektion.SOUVERAENITAETS_SEKTION)
        self.assertEqual(klausel.prozedur, AktProzedur.VOLLVERFAHREN)
        self.assertTrue(klausel.operative)

    def test_kki_souveraenitaets_akt_aggregates_akt_signal(self) -> None:
        akt = build_souveraenitaets_akt(akt_id="akt-208-signal")

        self.assertEqual(akt.akt_signal.status, "akt-suspendiert")
        self.assertEqual(akt.suspendiert_klausel_ids, ("akt-208-signal-stability-lane",))
        self.assertEqual(akt.ratifiziert_klausel_ids, ("akt-208-signal-governance-lane",))
        self.assertEqual(akt.souveraen_klausel_ids, ("akt-208-signal-expansion-lane",))

    def test_kki_grundrechts_charta_builds_ausgesetzt_schutz_artikel(self) -> None:
        charta = build_grundrechts_charta(charta_id="charta-207-stability")
        artikel = next(a for a in charta.artikel if a.geltung is ChartaGeltung.AUSGESETZT)

        self.assertIsInstance(charta, GrundrechtsCharta)
        self.assertIsInstance(artikel, ChartaArtikel)
        self.assertEqual(artikel.kapitel, ChartaKapitel.SCHUTZ_KAPITEL)
        self.assertEqual(artikel.verfahren, ChartaVerfahren.DRINGLICHE_EINTRAGUNG)
        self.assertGreaterEqual(artikel.ratification_depth, 1)

    def test_kki_grundrechts_charta_builds_geltend_ordnungs_artikel(self) -> None:
        charta = build_grundrechts_charta(charta_id="charta-207-governance")
        artikel = next(a for a in charta.artikel if a.geltung is ChartaGeltung.GELTEND)

        self.assertEqual(artikel.kapitel, ChartaKapitel.ORDNUNGS_KAPITEL)
        self.assertEqual(artikel.verfahren, ChartaVerfahren.ORDENTLICHE_EINTRAGUNG)
        self.assertGreater(artikel.codex_weight, 0.45)

    def test_kki_grundrechts_charta_builds_grundrecht_souveraenitaets_artikel(self) -> None:
        charta = build_grundrechts_charta(charta_id="charta-207-expansion")
        artikel = next(a for a in charta.artikel if a.geltung is ChartaGeltung.GRUNDRECHT)

        self.assertEqual(artikel.kapitel, ChartaKapitel.SOUVERAENITAETS_KAPITEL)
        self.assertEqual(artikel.verfahren, ChartaVerfahren.PLENARE_EINTRAGUNG)
        self.assertTrue(artikel.enforceable)

    def test_kki_grundrechts_charta_aggregates_charta_signal(self) -> None:
        charta = build_grundrechts_charta(charta_id="charta-207-signal")

        self.assertEqual(charta.charta_signal.status, "charta-ausgesetzt")
        self.assertEqual(charta.ausgesetzt_artikel_ids, ("charta-207-signal-stability-lane",))
        self.assertEqual(charta.geltend_artikel_ids, ("charta-207-signal-governance-lane",))
        self.assertEqual(charta.grundrecht_artikel_ids, ("charta-207-signal-expansion-lane",))

    def test_kki_verfassungs_senat_builds_ungueltig_schutz_mandat(self) -> None:
        senat = build_verfassungs_senat(senat_id="senat-206-stability")
        mandat = next(m for m in senat.mandate if m.beschluss is SenatsBeschluss.UNGUELTIG)

        self.assertIsInstance(senat, VerfassungsSenat)
        self.assertIsInstance(mandat, SenatsMandat)
        self.assertEqual(mandat.fraktion, SenatsFraktion.SCHUTZ_FRAKTION)
        self.assertEqual(mandat.sitzung, SenatsSitzung.DRINGLICH_SITZUNG)
        self.assertGreaterEqual(mandat.deliberation_quorum, 1)

    def test_kki_verfassungs_senat_builds_wirksam_ordnungs_mandat(self) -> None:
        senat = build_verfassungs_senat(senat_id="senat-206-governance")
        mandat = next(m for m in senat.mandate if m.beschluss is SenatsBeschluss.WIRKSAM)

        self.assertEqual(mandat.fraktion, SenatsFraktion.ORDNUNGS_FRAKTION)
        self.assertEqual(mandat.sitzung, SenatsSitzung.ORDENTLICHE_SITZUNG)
        self.assertGreater(mandat.resolution_weight, 0.45)

    def test_kki_verfassungs_senat_builds_grundlegend_souveraenitaets_mandat(self) -> None:
        senat = build_verfassungs_senat(senat_id="senat-206-expansion")
        mandat = next(m for m in senat.mandate if m.beschluss is SenatsBeschluss.GRUNDLEGEND)

        self.assertEqual(mandat.fraktion, SenatsFraktion.SOUVERAENITAETS_FRAKTION)
        self.assertEqual(mandat.sitzung, SenatsSitzung.PLENARSITZUNG)
        self.assertTrue(mandat.binding)

    def test_kki_verfassungs_senat_aggregates_senat_signal(self) -> None:
        senat = build_verfassungs_senat(senat_id="senat-206-signal")

        self.assertEqual(senat.senat_signal.status, "senat-ungueltig")
        self.assertEqual(senat.ungueltig_mandat_ids, ("senat-206-signal-stability-lane",))
        self.assertEqual(senat.wirksam_mandat_ids, ("senat-206-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_mandat_ids, ("senat-206-signal-expansion-lane",))

    def test_kki_normen_tribunal_builds_abgewiesen_schutz_fall(self) -> None:
        tribunal = build_normen_tribunal(tribunal_id="tribunal-205-stability")
        fall = next(f for f in tribunal.faelle if f.urteil is TribunalUrteil.ABGEWIESEN)

        self.assertIsInstance(tribunal, NormenTribunal)
        self.assertIsInstance(fall, TribunalFall)
        self.assertEqual(fall.kammer, TribunalKammer.SCHUTZ_KAMMER)
        self.assertEqual(fall.verfahren, TribunalVerfahren.SUMMARISCHES_VERFAHREN)
        self.assertGreaterEqual(fall.deliberation_rounds, 1)

    def test_kki_normen_tribunal_builds_bestaetigt_ordnungs_fall(self) -> None:
        tribunal = build_normen_tribunal(tribunal_id="tribunal-205-governance")
        fall = next(f for f in tribunal.faelle if f.urteil is TribunalUrteil.BESTAETIGT)

        self.assertEqual(fall.kammer, TribunalKammer.ORDNUNGS_KAMMER)
        self.assertEqual(fall.verfahren, TribunalVerfahren.ORDENTLICHES_VERFAHREN)
        self.assertGreater(fall.verdict_weight, 0.45)

    def test_kki_normen_tribunal_builds_verfassungsgebunden_souveraenitaets_fall(self) -> None:
        tribunal = build_normen_tribunal(tribunal_id="tribunal-205-expansion")
        fall = next(f for f in tribunal.faelle if f.urteil is TribunalUrteil.VERFASSUNGSGEBUNDEN)

        self.assertEqual(fall.kammer, TribunalKammer.SOUVERAENITAETS_KAMMER)
        self.assertEqual(fall.verfahren, TribunalVerfahren.VERFASSUNGSVERFAHREN)
        self.assertTrue(fall.release_ready)

    def test_kki_normen_tribunal_aggregates_tribunal_signal(self) -> None:
        tribunal = build_normen_tribunal(tribunal_id="tribunal-205-signal")

        self.assertEqual(tribunal.tribunal_signal.status, "tribunal-abgewiesen")
        self.assertEqual(tribunal.abgewiesen_fall_ids, ("tribunal-205-signal-stability-lane",))
        self.assertEqual(tribunal.bestaetigt_fall_ids, ("tribunal-205-signal-governance-lane",))
        self.assertEqual(tribunal.verfassungsgebunden_fall_ids, ("tribunal-205-signal-expansion-lane",))

    def test_kki_protocol_context_defaults_idempotency(self) -> None:
        context = protocol_context("corr-001", sequence=3)

        self.assertIsInstance(context, ProtocolContext)
        self.assertEqual(context.correlation_id, "corr-001")
        self.assertTrue(context.idempotency_key.startswith("msg-"))
        self.assertEqual(context.sequence, 3)

    def test_kki_command_message_is_acknowledged(self) -> None:
        message = command_message(
            name="approve-rollout",
            source_boundary="governance",
            target_boundary="rollout",
            correlation_id="corr-cmd",
            payload={"decision": "approve"},
        )

        self.assertIsInstance(message, MessageEnvelope)
        self.assertEqual(message.kind, MessageKind.COMMAND)
        self.assertEqual(message.delivery_mode, DeliveryMode.SYNC)
        self.assertEqual(message.delivery_guarantee, DeliveryGuarantee.ACKNOWLEDGED)

    def test_kki_event_message_is_replayable(self) -> None:
        event = event_message(
            name="shadow-drift-detected",
            event_class="shadow",
            severity="warning",
            source_boundary="shadow",
            target_boundary="telemetry",
            correlation_id="corr-evt",
            payload={"delta": 0.12},
        )

        self.assertIsInstance(event, EventEnvelope)
        self.assertEqual(event.message.kind, MessageKind.EVENT)
        self.assertEqual(event.message.delivery_mode, DeliveryMode.ASYNC)
        self.assertEqual(event.message.delivery_guarantee, DeliveryGuarantee.REPLAYABLE)
        self.assertTrue(event.replayable)

    def test_kki_transfer_message_wraps_transfer_envelope(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = core_state_for_runtime(dna, module="orchestration", status="handoff", budget=0.54)
        envelope = transfer_envelope_for_state(
            state,
            target_boundary="recovery",
            correlation_id="corr-transfer",
            sequence=4,
        )
        message = transfer_message(envelope, name="state-handoff")

        self.assertEqual(message.kind, MessageKind.TRANSFER)
        self.assertEqual(message.delivery_guarantee, DeliveryGuarantee.REPLAYABLE)
        self.assertEqual(message.context.sequence, 4)
        self.assertEqual(message.payload["payload"]["status"], "handoff")

    def test_kki_evidence_message_is_proof_bound(self) -> None:
        evidence = EvidenceRecord(
            evidence_type="recovery-approval",
            subject="restart-sequence",
            correlation_id="corr-proof",
            audit_ref="audit-proof",
            payload={"approved": True},
        )
        message = evidence_message(
            evidence,
            source_boundary="governance",
            target_boundary="telemetry",
        )

        self.assertEqual(message.kind, MessageKind.EVIDENCE)
        self.assertEqual(message.delivery_guarantee, DeliveryGuarantee.PROOF_BOUND)
        self.assertEqual(message.integrity_status, "attested")

    def test_kki_observer_identity_can_observe_events(self) -> None:
        identity = AuthorizationIdentity(
            slug="observer-1",
            kind=IdentityKind.OPERATOR,
            role=RoleName.OBSERVER,
            trust_level=TrustLevel.RESTRICTED,
            boundary_scope=("telemetry",),
        )
        event = event_message(
            name="telemetry-pulse",
            event_class="telemetry",
            severity="info",
            source_boundary="telemetry",
            target_boundary="governance",
            correlation_id="corr-observe",
            payload={"heartbeat": True},
        )

        decision = authorize_action(
            identity,
            action=ActionName.OBSERVE,
            boundary="telemetry",
            message=event.message,
        )

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.permission_source, "role-policy")

    def test_kki_gatekeeper_quarantine_requires_evidence(self) -> None:
        identity = AuthorizationIdentity(
            slug="gatekeeper-1",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.PRIVILEGED,
            boundary_scope=("security", "shadow", "rollout"),
        )

        denied = authorize_action(
            identity,
            action="quarantine",
            boundary="security",
        )
        allowed = authorize_action(
            identity,
            action="quarantine",
            boundary="security",
            evidence_ref="audit-quarantine-1",
        )

        self.assertFalse(denied.allowed)
        self.assertTrue(allowed.allowed)
        self.assertTrue(allowed.requires_evidence)

    def test_kki_supervisor_override_requires_commitment(self) -> None:
        identity = AuthorizationIdentity(
            slug="supervisor-1",
            kind=IdentityKind.SUPERVISOR,
            role=RoleName.SUPERVISOR,
            trust_level=TrustLevel.EMERGENCY,
            boundary_scope=("security", "governance", "recovery"),
        )

        denied = authorize_action(
            identity,
            action="override",
            boundary="governance",
            operating_mode=OperatingMode.EMERGENCY,
            evidence_ref="audit-override-1",
        )
        allowed = authorize_action(
            identity,
            action="override",
            boundary="governance",
            operating_mode=OperatingMode.EMERGENCY,
            evidence_ref="audit-override-1",
            commitment_ref="commit-override-1",
        )

        self.assertFalse(denied.allowed)
        self.assertTrue(allowed.allowed)
        self.assertTrue(allowed.escalation_required)

    def test_kki_delegation_is_bounded_and_time_limited(self) -> None:
        identity = AuthorizationIdentity(
            slug="runtime-cell-1",
            kind=IdentityKind.RUNTIME,
            role=RoleName.OBSERVER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("orchestration",),
        )
        delegation = DelegationGrant(
            grantor_slug="operator-1",
            delegate_slug="runtime-cell-1",
            action=ActionName.EXECUTE,
            boundaries=("orchestration",),
            operating_modes=(OperatingMode.NORMAL,),
            message_kinds=(MessageKind.COMMAND,),
            expires_at="2099-01-01T00:00:00+00:00",
            justification="temporary rollout assist",
        )

        decision = authorize_action(
            identity,
            action="execute",
            boundary="orchestration",
            delegation=delegation,
        )

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.permission_source, "delegation")

    def test_kki_delegation_does_not_grant_critical_override(self) -> None:
        identity = AuthorizationIdentity(
            slug="operator-2",
            kind=IdentityKind.OPERATOR,
            role=RoleName.OBSERVER,
            trust_level=TrustLevel.EMERGENCY,
            boundary_scope=("governance",),
        )
        delegation = DelegationGrant(
            grantor_slug="supervisor-2",
            delegate_slug="operator-2",
            action=ActionName.OVERRIDE,
            boundaries=("governance",),
            operating_modes=(OperatingMode.EMERGENCY,),
            message_kinds=(MessageKind.COMMAND,),
            expires_at="2099-01-01T00:00:00+00:00",
            justification="should remain disallowed",
        )

        decision = authorize_action(
            identity,
            action="override",
            boundary="governance",
            operating_mode=OperatingMode.EMERGENCY,
            evidence_ref="audit-override-2",
            commitment_ref="commit-override-2",
            delegation=delegation,
        )

        self.assertFalse(decision.allowed)

    def test_kki_control_plane_loads_scoped_artifacts(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="base-runtime",
                kind=ArtifactKind.BASE_CONFIG,
                version="1.0",
                scope=ArtifactScope.GLOBAL,
                payload={"budget": 0.7, "telemetry": True},
            ),
            ControlArtifact(
                artifact_id="pilot-runtime",
                kind=ArtifactKind.BASE_CONFIG,
                version="1.1",
                scope=ArtifactScope.STAGE,
                runtime_stage=RuntimeStage.PILOT,
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                payload={"budget": 0.76},
            ),
            ControlArtifact(
                artifact_id="security-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="security",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-policy-1",
                payload={"quarantine_mode": "strict"},
            ),
        )

        loaded = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="security")

        self.assertIsInstance(loaded, LoadedControlPlane)
        self.assertEqual(loaded.effective_payload["budget"], 0.76)
        self.assertEqual(loaded.effective_payload["quarantine_mode"], "strict")
        self.assertEqual(len(loaded.applied_artifacts), 3)

    def test_kki_policy_artifacts_require_evidence(self) -> None:
        with self.assertRaises(ValueError):
            ControlArtifact(
                artifact_id="security-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                boundary="security",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY),
                payload={"quarantine_mode": "strict"},
            )

    def test_kki_emergency_override_requires_rollback(self) -> None:
        with self.assertRaises(ValueError):
            ControlArtifact(
                artifact_id="emergency-stop",
                kind=ArtifactKind.EMERGENCY_OVERRIDE,
                version="3.0",
                scope=ArtifactScope.ROLE,
                runtime_stage=RuntimeStage.PRODUCTION,
                boundary="governance",
                role_scope="supervisor",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-stop-1",
                commitment_ref="commit-stop-1",
                payload={"stop_rollout": True},
            )

    def test_kki_policy_distribution_uses_gatekeeper_approval(self) -> None:
        identity = AuthorizationIdentity(
            slug="gatekeeper-2",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.PRIVILEGED,
            boundary_scope=("security",),
        )
        artifact = ControlArtifact(
            artifact_id="security-policy",
            kind=ArtifactKind.POLICY,
            version="2.1",
            scope=ArtifactScope.BOUNDARY,
            boundary="security",
            validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY),
            evidence_ref="audit-policy-2",
            payload={"quarantine_mode": "strict"},
        )

        decision = authorize_artifact(identity, artifact)

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.action, ActionName.APPROVE)

    def test_kki_loader_rejects_inconsistent_distribution_versions(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="pilot-runtime",
                kind=ArtifactKind.BASE_CONFIG,
                version="1.0",
                scope=ArtifactScope.STAGE,
                runtime_stage=RuntimeStage.PILOT,
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                payload={"budget": 0.74},
            ),
            ControlArtifact(
                artifact_id="pilot-runtime",
                kind=ArtifactKind.BASE_CONFIG,
                version="1.1",
                scope=ArtifactScope.STAGE,
                runtime_stage=RuntimeStage.PILOT,
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                payload={"budget": 0.76},
            ),
        )

        with self.assertRaises(ValueError):
            load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT)

    def test_kki_telemetry_signal_projects_event(self) -> None:
        event = event_message(
            name="policy-drift",
            event_class="telemetry",
            severity="warning",
            source_boundary="telemetry",
            target_boundary="governance",
            correlation_id="corr-telemetry",
            payload={"drift": 0.18},
        )

        signal = telemetry_signal_from_event(
            event,
            metrics={"drift_ratio": 0.18},
            labels={"dashboard": "ops"},
        )

        self.assertIsInstance(signal, TelemetrySignal)
        self.assertEqual(signal.boundary, ModuleBoundaryName.TELEMETRY)
        self.assertEqual(signal.metrics["drift_ratio"], 0.18)
        self.assertEqual(signal.labels["event_class"], "telemetry")

    def test_kki_telemetry_alert_tracks_thresholds(self) -> None:
        alert = telemetry_alert(
            alert_key="policy-drift-warning",
            boundary="security",
            severity="warning",
            summary="Policy drift exceeds warning budget",
            observed_value=0.18,
            threshold=0.1,
            correlation_id="corr-alert",
        )

        self.assertIsInstance(alert, TelemetryAlert)
        self.assertEqual(alert.status, "open")
        self.assertEqual(alert.boundary, ModuleBoundaryName.SECURITY)

    def test_kki_audit_entry_is_created_from_message(self) -> None:
        message = command_message(
            name="promote-artifact",
            source_boundary="governance",
            target_boundary="rollout",
            correlation_id="corr-audit-msg",
            payload={"artifact": "pilot-runtime"},
        )

        entry = audit_entry_for_message(message)

        self.assertIsInstance(entry, AuditTrailEntry)
        self.assertEqual(entry.subject, "promote-artifact")
        self.assertEqual(entry.payload["delivery_guarantee"], "acknowledged")

    def test_kki_audit_entry_is_created_from_artifact(self) -> None:
        artifact = ControlArtifact(
            artifact_id="security-policy",
            kind=ArtifactKind.POLICY,
            version="2.2",
            scope=ArtifactScope.BOUNDARY,
            boundary="security",
            validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY),
            evidence_ref="audit-policy-22",
            payload={"quarantine_mode": "strict"},
        )

        entry = audit_entry_for_artifact(artifact)

        self.assertEqual(entry.entry_type, "control-artifact")
        self.assertEqual(entry.payload["artifact_kind"], "policy")
        self.assertEqual(entry.evidence_ref, "audit-policy-22")

    def test_kki_telemetry_snapshot_aggregates_views(self) -> None:
        signal = TelemetrySignal(
            signal_name="policy-drift",
            boundary=ModuleBoundaryName.TELEMETRY,
            correlation_id="corr-snapshot",
            severity="warning",
            status="observed",
            metrics={"drift_ratio": 0.15},
        )
        alert = TelemetryAlert(
            alert_key="policy-drift-warning",
            boundary=ModuleBoundaryName.SECURITY,
            severity="warning",
            summary="Policy drift exceeds warning budget",
            observed_value=0.15,
            threshold=0.1,
            correlation_id="corr-snapshot",
        )
        snapshot = build_telemetry_snapshot(
            runtime_stage=RuntimeStage.PILOT,
            signals=(signal,),
            alerts=(alert,),
            active_controls=("pilot-runtime", "security-policy"),
        )

        self.assertIsInstance(snapshot, TelemetrySnapshot)
        self.assertEqual(snapshot.highest_severity(), "warning")
        self.assertEqual(snapshot.status_counts()["observed"], 1)
        self.assertIn("security-policy", snapshot.to_dict()["active_controls"])

    def test_kki_shadow_preview_tracks_controls_and_invariants(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = core_state_for_runtime(dna, module="orchestration", status="ready", budget=0.72)
        control_plane = load_control_plane(
            (
                ControlArtifact(
                    artifact_id="pilot-runtime",
                    kind=ArtifactKind.BASE_CONFIG,
                    version="1.1",
                    scope=ArtifactScope.STAGE,
                    runtime_stage=RuntimeStage.PILOT,
                    validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                    payload={"budget": 0.76},
                ),
            ),
            runtime_stage=RuntimeStage.PILOT,
        )
        command = command_message(
            name="promote-shadow-build",
            source_boundary="governance",
            target_boundary="rollout",
            correlation_id="corr-shadow-1",
            payload={"wave": "pilot"},
        )

        preview = shadow_preview_for_command(
            state,
            command,
            control_plane,
            mode=PreviewMode.SHADOW,
            invariants=("no-live-cutover",),
        )

        self.assertIsInstance(preview, ShadowPreview)
        self.assertEqual(preview.control_versions, ("1.1",))
        self.assertIn("no-live-cutover", preview.invariants)

    def test_kki_dry_run_evaluation_emits_warning_on_drift(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = core_state_for_runtime(dna, module="orchestration", status="ready", budget=0.6)
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.SHADOW)
        command = command_message(
            name="replay-state",
            source_boundary="orchestration",
            target_boundary="shadow",
            correlation_id="corr-shadow-2",
            payload={"replay": True},
        )
        preview = shadow_preview_for_command(state, command, control_plane, mode=PreviewMode.DRY_RUN)

        evaluation = evaluate_dry_run(preview, observed_budget=0.78, drift_threshold=0.1)

        self.assertEqual(evaluation.status, "drift")
        self.assertFalse(evaluation.replay_ready)
        self.assertIsNotNone(evaluation.alert)

    def test_kki_shadow_snapshot_builds_drilldown_view(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = core_state_for_runtime(dna, module="orchestration", status="ready", budget=0.7)
        artifacts = (
            ControlArtifact(
                artifact_id="pilot-runtime",
                kind=ArtifactKind.BASE_CONFIG,
                version="1.1",
                scope=ArtifactScope.STAGE,
                runtime_stage=RuntimeStage.PILOT,
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                payload={"budget": 0.76},
            ),
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-1",
                payload={"dry_run_mode": "strict"},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        command = command_message(
            name="validate-cutover",
            source_boundary="governance",
            target_boundary="shadow",
            correlation_id="corr-shadow-3",
            payload={"cutover": "candidate"},
        )
        preview = shadow_preview_for_command(state, command, control_plane)
        evaluation = evaluate_dry_run(preview, observed_budget=0.68, drift_threshold=0.05)

        snapshot = shadow_snapshot(preview, evaluation, control_plane)

        self.assertIsInstance(snapshot, TelemetrySnapshot)
        self.assertIn("shadow-policy", snapshot.to_dict()["active_controls"])
        self.assertGreaterEqual(len(snapshot.audit_entries), 2)

    def test_kki_shadow_event_emits_shadow_classification(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = core_state_for_runtime(dna, module="orchestration", status="preview", budget=0.64)
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.SHADOW)
        command = command_message(
            name="preview-rollout",
            source_boundary="orchestration",
            target_boundary="shadow",
            correlation_id="corr-shadow-4",
            payload={"wave": "preview"},
        )
        preview = shadow_preview_for_command(state, command, control_plane)
        evaluation = evaluate_dry_run(preview, observed_budget=0.63, drift_threshold=0.05)

        event = shadow_event(preview, evaluation)

        self.assertIsInstance(event, EventEnvelope)
        self.assertEqual(event.event_class, "shadow")
        self.assertEqual(event.message.target_boundary, ModuleBoundaryName.TELEMETRY)

    def test_kki_recovery_checkpoint_captures_state_and_transfer(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = core_state_for_runtime(dna, module="orchestration", status="degraded", budget=0.52)

        checkpoint = recovery_checkpoint_for_state(state, correlation_id="corr-recovery-1")

        self.assertIsInstance(checkpoint, RecoveryCheckpoint)
        self.assertEqual(checkpoint.persistence_record.retention_class, "restart")
        self.assertEqual(checkpoint.transfer_envelope.target_boundary, ModuleBoundaryName.RECOVERY)

    def test_kki_rollback_directive_uses_control_plane_chain(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = core_state_for_runtime(dna, module="rollout", status="rollback", budget=0.48)
        checkpoint = recovery_checkpoint_for_state(state, correlation_id="corr-recovery-2")
        control_plane = load_control_plane(
            (
                ControlArtifact(
                    artifact_id="pilot-runtime",
                    kind=ArtifactKind.BASE_CONFIG,
                    version="1.1",
                    scope=ArtifactScope.STAGE,
                    runtime_stage=RuntimeStage.PILOT,
                    validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                    rollback_version="1.0",
                    payload={"budget": 0.76},
                ),
            ),
            runtime_stage=RuntimeStage.PILOT,
        )

        directive = rollback_directive_for_checkpoint(checkpoint, control_plane, reason="shadow drift")

        self.assertIsInstance(directive, RollbackDirective)
        self.assertEqual(directive.mode, RecoveryMode.ROLLBACK)
        self.assertEqual(directive.rollback_chain, ("pilot-runtime:1.0",))

    def test_kki_rollback_directive_falls_back_without_versions(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = core_state_for_runtime(dna, module="shadow", status="blocked", budget=0.44)
        checkpoint = recovery_checkpoint_for_state(state, correlation_id="corr-recovery-3")
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.SHADOW)

        directive = rollback_directive_for_checkpoint(
            checkpoint,
            control_plane,
            reason="missing preview guarantees",
            mode=RecoveryMode.RESTART,
        )

        self.assertEqual(directive.rollback_chain, ("state-only-recovery",))
        self.assertEqual(directive.mode, RecoveryMode.RESTART)

    def test_kki_recovery_outcome_binds_evidence_and_snapshot(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = core_state_for_runtime(dna, module="rollout", status="rollback", budget=0.46)
        checkpoint = recovery_checkpoint_for_state(state, correlation_id="corr-recovery-4")
        control_plane = load_control_plane(
            (
                ControlArtifact(
                    artifact_id="rollout-policy",
                    kind=ArtifactKind.POLICY,
                    version="2.0",
                    scope=ArtifactScope.BOUNDARY,
                    runtime_stage=RuntimeStage.PILOT,
                    boundary="rollout",
                    validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                    evidence_ref="audit-rollout-2",
                    rollback_version="1.9",
                    payload={"cutover_gate": "hold"},
                ),
            ),
            runtime_stage=RuntimeStage.PILOT,
            boundary="rollout",
        )
        directive = rollback_directive_for_checkpoint(checkpoint, control_plane, reason="pilot drift")

        outcome = recovery_outcome(
            directive,
            checkpoint,
            control_plane,
            replay_ready=True,
            audit_ref="audit-recovery-4",
            commitment_ref="commit-recovery-4",
        )

        self.assertIsInstance(outcome, RecoveryOutcome)
        self.assertEqual(outcome.status, "reentry-ready")
        self.assertEqual(outcome.evidence.commitment_ref, "commit-recovery-4")
        self.assertIn("rollout-policy", outcome.snapshot.to_dict()["active_controls"])

    def test_kki_integrated_smoke_build_runs_end_to_end(self) -> None:
        smoke = run_integrated_smoke_build(correlation_id="corr-integrated-1")

        self.assertIsInstance(smoke, IntegratedSmokeBuild)
        self.assertTrue(smoke.success)
        self.assertEqual(smoke.shadow_event.event_class, "shadow")
        self.assertEqual(smoke.recovery_outcome.status, "reentry-ready")

    def test_kki_integrated_smoke_build_keeps_controls_and_audit_visible(self) -> None:
        smoke = run_integrated_smoke_build(correlation_id="corr-integrated-2")
        exported = smoke.to_dict()

        self.assertIn("shadow-policy", exported["final_snapshot"]["active_controls"])
        self.assertIn("rollout-policy", exported["final_snapshot"]["active_controls"])
        self.assertGreaterEqual(len(exported["final_snapshot"]["audit_entries"]), 3)
        self.assertEqual(exported["final_snapshot"]["highest_severity"], "info")

    def test_kooperation_test_is_reproducible(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            first_result = self.run_script("kooperation_test.py", output_dir, seed=123)
            second_result = self.run_script("kooperation_test.py", output_dir, seed=123)

        self.assert_successful_run(first_result)
        self.assert_successful_run(second_result)
        self.assertEqual(first_result.stdout, second_result.stdout)
        self.assertIn("Seed: 123 (KKI_SEED)", first_result.stdout)

    def test_kooperation_visual_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script("kooperation_visual.py", output_dir, seed=99)
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_kooperation_graph.png").exists())
            self.assertIn("Graph gespeichert:", result.stdout)

    def test_schwarm_simulation_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script("schwarm_simulation.py", output_dir, seed=7)
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_schwarm_simulation.png").exists())
            self.assertIn("ERGEBNISSE", result.stdout)

    def test_commitment_protokoll_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script("commitment_protokoll.py", output_dir, seed=11)
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_commitment_protokoll.png").exists())
            self.assertIn("COMMITMENT-PROTOKOLL", result.stdout)

    def test_schwarm_polarisierung_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script("schwarm_polarisierung.py", output_dir, seed=17)
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_polarisierung.png").exists())
            self.assertIn("Polarisierungs-Index", result.stdout)

    def test_schwarm_polarisierung_adaptiv_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_polarisierung.py",
                output_dir,
                seed=19,
                extra_env={
                    "KKI_REWIRING_ENABLED": "true",
                    "KKI_REWIRE_REP_THRESHOLD": "0.30",
                    "KKI_REWIRE_PROXIMITY_WEIGHT": "0.35",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_polarisierung.png").exists())
            self.assertIn("Adaptives Rewiring: aktiv", result.stdout)

    def test_schwarm_parameterstudie_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script("schwarm_parameterstudie.py", output_dir, seed=23)
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_netzwerk_parameterstudie.png").exists())
            self.assertIn("Beste Konfiguration", result.stdout)

    def test_schwarm_adaptive_netzwerke_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_adaptive_netzwerke.py",
                output_dir,
                seed=29,
                extra_env={"KKI_ADAPTIVE_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_adaptive_netzwerke.png").exists())
            self.assertIn("Beste adaptive Konfiguration", result.stdout)

    def test_schwarm_invasive_netzwerke_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_invasive_netzwerke.py",
                output_dir,
                seed=31,
                extra_env={"KKI_INVASION_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_invasive_netzwerke.png").exists())
            self.assertIn("Beste adaptive Abwehr", result.stdout)

    def test_schwarm_commitment_resilienz_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_commitment_resilienz.py",
                output_dir,
                seed=37,
                extra_env={"KKI_COMMITMENT_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_commitment_resilienz.png").exists())
            self.assertIn("Beste adaptive Commitment-Abwehr", result.stdout)

    def test_schwarm_vertrauens_benchmark_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_vertrauens_benchmark.py",
                output_dir,
                seed=41,
                extra_env={"KKI_BENCHMARK_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_vertrauens_benchmark.png").exists())
            self.assertIn("Beste Vertrauensstrategie", result.stdout)

    def test_schwarm_grossstudie_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_grossstudie.py",
                output_dir,
                seed=43,
                extra_env={"KKI_MEGASTUDY_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_grossstudie.png").exists())
            self.assertIn("Staerkster adaptiver Vorteil", result.stdout)

    def test_schwarm_anti_polarisierung_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_anti_polarisierung.py",
                output_dir,
                seed=47,
                extra_env={"KKI_ANTI_POL_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_anti_polarisierung.png").exists())
            self.assertIn("Beste Anti-Polarisierungsstrategie", result.stdout)

    def test_schwarm_gekoppelte_abwehr_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_gekoppelte_abwehr.py",
                output_dir,
                seed=53,
                extra_env={"KKI_COUPLED_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_gekoppelte_abwehr.png").exists())
            self.assertIn("Beste gekoppelte Abwehrarchitektur", result.stdout)

    def test_schwarm_rollenspezialisierung_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_rollenspezialisierung.py",
                output_dir,
                seed=59,
                extra_env={"KKI_ROLLENSPEZ_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_rollenspezialisierung.png").exists())
            self.assertIn("Bestes Rollenprofil", result.stdout)

    def test_schwarm_rollenlernen_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_rollenlernen.py",
                output_dir,
                seed=61,
                extra_env={"KKI_ROLLENLERNEN_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_rollenlernen.png").exists())
            self.assertIn("Bestes Lernprofil", result.stdout)

    def test_schwarm_rollenwechsel_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_rollenwechsel.py",
                output_dir,
                seed=67,
                extra_env={
                    "KKI_ROLLENWECHSEL_REPETITIONS": "1",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_rollenwechsel.png").exists())
            self.assertIn("Bestes Rollenwechselprofil", result.stdout)

    def test_schwarm_missionsziele_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_missionsziele.py",
                output_dir,
                seed=71,
                extra_env={
                    "KKI_MISSION_REPETITIONS": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_missionsziele.png").exists())
            self.assertIn("Beste Missionsarchitektur", result.stdout)

    def test_schwarm_missionskonflikte_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_missionskonflikte.py",
                output_dir,
                seed=73,
                extra_env={
                    "KKI_MISSION_ARBITRATION_REPETITIONS": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_missionskonflikte.png").exists())
            self.assertIn("Beste Konflikt-Architektur", result.stdout)

    def test_schwarm_arbeitsketten_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_arbeitsketten.py",
                output_dir,
                seed=79,
                extra_env={
                    "KKI_WORKFLOW_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_arbeitsketten.png").exists())
            self.assertIn("Beste Workflow-Architektur", result.stdout)

    def test_schwarm_arbeitszellen_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_arbeitszellen.py",
                output_dir,
                seed=83,
                extra_env={
                    "KKI_WORKFLOW_CELL_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_arbeitszellen.png").exists())
            self.assertIn("Beste Zellarchitektur", result.stdout)

    def test_schwarm_arbeitszellen_parallel_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_arbeitszellen_parallel.py",
                output_dir,
                seed=89,
                extra_env={
                    "KKI_PARALLEL_CELLS_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_arbeitszellen_parallel.png").exists())
            self.assertIn("Beste Ressourcenarchitektur", result.stdout)

    def test_schwarm_faehigkeitscluster_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_faehigkeitscluster.py",
                output_dir,
                seed=97,
                extra_env={
                    "KKI_CAPABILITY_CLUSTER_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_faehigkeitscluster.png").exists())
            self.assertIn("Beste Clusterarchitektur", result.stdout)

    def test_schwarm_engpassmanagement_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_engpassmanagement.py",
                output_dir,
                seed=101,
                extra_env={
                    "KKI_BOTTLENECK_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_engpassmanagement.png").exists())
            self.assertIn("Bestes Engpassprofil", result.stdout)

    def test_schwarm_meta_koordination_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_meta_koordination.py",
                output_dir,
                seed=103,
                extra_env={
                    "KKI_META_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_meta_koordination.png").exists())
            self.assertIn("Beste Meta-Architektur", result.stdout)





    def test_schwarm_integrationsstudie_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_integrationsstudie.py",
                output_dir,
                seed=131,
                extra_env={
                    "KKI_INTEGRATION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_integrationsstudie.png").exists())
            self.assertIn("Beste Gesamtarchitektur", result.stdout)

    def test_schwarm_wiederanlauf_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_wiederanlauf.py",
                output_dir,
                seed=127,
                extra_env={
                    "KKI_RESTART_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_wiederanlauf.png").exists())
            self.assertIn("Beste Wiederanlauf-Architektur", result.stdout)

    def test_schwarm_fehlerisolation_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_fehlerisolation.py",
                output_dir,
                seed=113,
                extra_env={
                    "KKI_ISOLATION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_fehlerisolation.png").exists())
            self.assertIn("Beste Isolationsarchitektur", result.stdout)

    def test_schwarm_spezialfaehigkeiten_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_spezialfaehigkeiten.py",
                output_dir,
                seed=109,
                extra_env={
                    "KKI_SKILL_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_spezialfaehigkeiten.png").exists())
            self.assertIn("Beste Lernarchitektur", result.stdout)

    def test_schwarm_manipulationsresistenz_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_manipulationsresistenz.py",
                output_dir,
                seed=107,
                extra_env={
                    "KKI_MANIPULATION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_manipulationsresistenz.png").exists())
            self.assertIn("Beste Abwehrarchitektur", result.stdout)

    def test_schwarm_interaktionsmodelle_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_interaktionsmodelle.py",
                output_dir,
                seed=139,
                extra_env={
                    "KKI_INTERACTION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_interaktionsmodelle.png").exists())
            self.assertIn("Bestes Interaktionsmodell", result.stdout)

    def test_schwarm_modellwechsel_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_modellwechsel.py",
                output_dir,
                seed=149,
                extra_env={
                    "KKI_MODEL_SWITCH_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_modellwechsel.png").exists())
            self.assertIn("Bestes Modellwechselprofil", result.stdout)

    def test_schwarm_beziehungsgedaechtnis_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_beziehungsgedaechtnis.py",
                output_dir,
                seed=151,
                extra_env={
                    "KKI_RELATIONSHIP_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_beziehungsgedaechtnis.png").exists())
            self.assertIn("Bestes Beziehungsgedaechtnisprofil", result.stdout)

    def test_schwarm_gruppenbildung_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_gruppenbildung.py",
                output_dir,
                seed=157,
                extra_env={
                    "KKI_GROUP_FORMATION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_gruppenbildung.png").exists())
            self.assertIn("Beste Gruppenarchitektur", result.stdout)

    def test_schwarm_gruppenidentitaet_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_gruppenidentitaet.py",
                output_dir,
                seed=163,
                extra_env={
                    "KKI_GROUP_IDENTITY_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_gruppenidentitaet.png").exists())
            self.assertIn("Beste Identitaetsarchitektur", result.stdout)

    def test_schwarm_gruppentalente_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_gruppentalente.py",
                output_dir,
                seed=167,
                extra_env={
                    "KKI_GROUP_TALENT_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_gruppentalente.png").exists())
            self.assertIn("Bestes Gruppentalentprofil", result.stdout)

    def test_schwarm_gruppenhandoff_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_gruppenhandoff.py",
                output_dir,
                seed=173,
                extra_env={
                    "KKI_GROUP_HANDOFF_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_gruppenhandoff.png").exists())
            self.assertIn("Bestes Gruppenhandoff-Profil", result.stdout)

    def test_schwarm_faehigkeitsarbitration_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_faehigkeitsarbitration.py",
                output_dir,
                seed=179,
                extra_env={
                    "KKI_CAPABILITY_ARBITRATION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_faehigkeitsarbitration.png").exists())
            self.assertIn("Beste Faehigkeitsarbitration", result.stdout)

    def test_schwarm_gruppenrobustheit_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_gruppenrobustheit.py",
                output_dir,
                seed=181,
                extra_env={
                    "KKI_GROUP_ROBUSTNESS_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_gruppenrobustheit.png").exists())
            self.assertIn("Beste Gruppenrobustheit", result.stdout)

    def test_schwarm_vorbauphase_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_vorbauphase.py",
                output_dir,
                seed=191,
                extra_env={
                    "KKI_PREBUILD_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_vorbauphase.png").exists())
            self.assertIn("Beste Vor-Bauphasen-Architektur", result.stdout)

    def test_schwarm_dna_schema_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_dna_schema.py",
                output_dir,
                seed=193,
                extra_env={
                    "KKI_DNA_SCHEMA_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_dna_schema.png").exists())
            self.assertIn("Beste DNA-Schema-Architektur", result.stdout)

    def test_schwarm_overlay_module_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_overlay_module.py",
                output_dir,
                seed=197,
                extra_env={
                    "KKI_OVERLAY_MODULE_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_overlay_module.png").exists())
            self.assertIn("Bestes Overlay-Modulprofil", result.stdout)

    def test_schwarm_gruppenbootstrap_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_gruppenbootstrap.py",
                output_dir,
                seed=199,
                extra_env={
                    "KKI_GROUP_BOOTSTRAP_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_gruppenbootstrap.png").exists())
            self.assertIn("Bestes Bootstrap-Profil", result.stdout)

    def test_schwarm_protokollstack_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_protokollstack.py",
                output_dir,
                seed=211,
                extra_env={
                    "KKI_PROTOCOL_STACK_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_protokollstack.png").exists())
            self.assertIn("Bester Protokollstack", result.stdout)

    def test_schwarm_handoff_vertraege_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_handoff_vertraege.py",
                output_dir,
                seed=223,
                extra_env={
                    "KKI_HANDOFF_CONTRACT_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_handoff_vertraege.png").exists())
            self.assertIn("Bester Handoff-Vertrag", result.stdout)

    def test_schwarm_governance_layer_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_governance_layer.py",
                output_dir,
                seed=227,
                extra_env={
                    "KKI_GOVERNANCE_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_governance_layer.png").exists())
            self.assertIn("Bester Governance-Layer", result.stdout)

    def test_schwarm_werkzeugbindung_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_werkzeugbindung.py",
                output_dir,
                seed=229,
                extra_env={
                    "KKI_TOOL_BINDING_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_werkzeugbindung.png").exists())
            self.assertIn("Beste Werkzeugbindung", result.stdout)

    def test_schwarm_laufzeitsupervision_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_laufzeitsupervision.py",
                output_dir,
                seed=233,
                extra_env={
                    "KKI_RUNTIME_SUPERVISION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_laufzeitsupervision.png").exists())
            self.assertIn("Beste Laufzeitsupervision", result.stdout)

    def test_schwarm_bauphasen_stresstest_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_bauphasen_stresstest.py",
                output_dir,
                seed=239,
                extra_env={
                    "KKI_BUILD_STRESS_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_bauphasen_stresstest.png").exists())
            self.assertIn("Bester Bauphasen-Stack", result.stdout)

    def test_schwarm_bauphasen_blueprint_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_bauphasen_blueprint.py",
                output_dir,
                seed=241,
                extra_env={
                    "KKI_BLUEPRINT_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_bauphasen_blueprint.png").exists())
            self.assertIn("Bester Bauphasen-Blueprint", result.stdout)

    def test_schwarm_runtime_dna_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_runtime_dna.py",
                output_dir,
                seed=251,
                extra_env={
                    "KKI_RUNTIME_DNA_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_runtime_dna.png").exists())
            self.assertIn("Beste Runtime-DNA", result.stdout)

    def test_schwarm_rollenassembler_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_rollenassembler.py",
                output_dir,
                seed=257,
                extra_env={
                    "KKI_ROLE_ASSEMBLER_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_rollenassembler.png").exists())
            self.assertIn("Bester Rollen-Assembler", result.stdout)

    def test_schwarm_werkzeugrouting_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_werkzeugrouting.py",
                output_dir,
                seed=263,
                extra_env={
                    "KKI_TOOL_ROUTING_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_werkzeugrouting.png").exists())
            self.assertIn("Bester Capability-Broker", result.stdout)

    def test_schwarm_wissensspeicher_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_wissensspeicher.py",
                output_dir,
                seed=269,
                extra_env={
                    "KKI_MEMORY_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_wissensspeicher.png").exists())
            self.assertIn("Bester Wissensspeicher", result.stdout)

    def test_schwarm_freigabe_workflow_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_freigabe_workflow.py",
                output_dir,
                seed=271,
                extra_env={
                    "KKI_APPROVAL_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_freigabe_workflow.png").exists())
            self.assertIn("Bester Freigabe-Workflow", result.stdout)

    def test_schwarm_supervisor_eingriffe_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_supervisor_eingriffe.py",
                output_dir,
                seed=277,
                extra_env={
                    "KKI_SUPERVISOR_ACTION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_supervisor_eingriffe.png").exists())
            self.assertIn("Bester Supervisor-Eingriff", result.stdout)

    def test_schwarm_resilienzbudget_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_resilienzbudget.py",
                output_dir,
                seed=281,
                extra_env={
                    "KKI_RESILIENCE_BUDGET_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_resilienzbudget.png").exists())
            self.assertIn("Bestes Resilienzbudget", result.stdout)

    def test_schwarm_sandbox_zellen_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_sandbox_zellen.py",
                output_dir,
                seed=307,
                extra_env={
                    "KKI_SANDBOX_CELL_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_sandbox_zellen.png").exists())
            self.assertIn("Beste Sandbox-Zellstruktur", result.stdout)

    def test_schwarm_missions_dry_run_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_missions_dry_run.py",
                output_dir,
                seed=331,
                extra_env={
                    "KKI_MISSION_DRY_RUN_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_missions_dry_run.png").exists())
            self.assertIn("Bester Missions-Dry-Run", result.stdout)

    def test_schwarm_bauphasen_pilot_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_bauphasen_pilot.py",
                output_dir,
                seed=359,
                extra_env={
                    "KKI_PILOT_ARCH_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_bauphasen_pilot.png").exists())
            self.assertIn("Beste Bauphasen-Pilotarchitektur", result.stdout)

    def test_schwarm_instanziierungspipeline_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_instanziierungspipeline.py",
                output_dir,
                seed=383,
                extra_env={
                    "KKI_INSTANTIATION_PIPELINE_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_instanziierungspipeline.png").exists())
            self.assertIn("Beste Instanziierungs-Pipeline", result.stdout)

    def test_schwarm_wissensbus_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_wissensbus.py",
                output_dir,
                seed=401,
                extra_env={
                    "KKI_KNOWLEDGE_BUS_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_wissensbus.png").exists())
            self.assertIn("Bester Wissensbus", result.stdout)

    def test_schwarm_werkzeugadapter_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_werkzeugadapter.py",
                output_dir,
                seed=419,
                extra_env={
                    "KKI_TOOL_ADAPTER_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_werkzeugadapter.png").exists())
            self.assertIn("Bester Werkzeug-Adapter", result.stdout)

    def test_schwarm_rollout_protokolle_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_rollout_protokolle.py",
                output_dir,
                seed=433,
                extra_env={
                    "KKI_ROLLOUT_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_rollout_protokolle.png").exists())
            self.assertIn("Bestes Rollout-Protokoll", result.stdout)

    def test_schwarm_zustandstransfer_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_zustandstransfer.py",
                output_dir,
                seed=449,
                extra_env={
                    "KKI_STATE_TRANSFER_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_zustandstransfer.png").exists())
            self.assertIn("Bester Zustandstransfer", result.stdout)

    def test_schwarm_ressourcen_orchestrator_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_ressourcen_orchestrator.py",
                output_dir,
                seed=461,
                extra_env={
                    "KKI_RESOURCE_ORCHESTRATOR_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_ressourcen_orchestrator.png").exists())
            self.assertIn("Bester Ressourcen-Orchestrator", result.stdout)

    def test_schwarm_audit_telemetrie_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_audit_telemetrie.py",
                output_dir,
                seed=467,
                extra_env={
                    "KKI_AUDIT_TELEMETRY_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_audit_telemetrie.png").exists())
            self.assertIn("Beste Audit-Telemetrie", result.stdout)

    def test_schwarm_sicherheits_policies_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_sicherheits_policies.py",
                output_dir,
                seed=479,
                extra_env={
                    "KKI_SECURITY_POLICY_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_sicherheits_policies.png").exists())
            self.assertIn("Beste Sicherheitskette", result.stdout)

    def test_schwarm_schattenbetrieb_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_schattenbetrieb.py",
                output_dir,
                seed=491,
                extra_env={
                    "KKI_SHADOW_MODE_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_schattenbetrieb.png").exists())
            self.assertIn("Bester Schattenbetrieb", result.stdout)

    def test_schwarm_bauphasen_rollout_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_bauphasen_rollout.py",
                output_dir,
                seed=503,
                extra_env={
                    "KKI_BUILD_ROLLOUT_FAST": "1",
                    "KKI_BUILD_ROLLOUT_REPETITIONS": "1",
                    "KKI_BUILD_ROLLOUT_AGENT_COUNT": "12",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_bauphasen_rollout.png").exists())
            self.assertIn("Bester Bauphasen-Rollout", result.stdout)


    # #341 FestkoerperFeld
    def test_kki_festkoerper_feld_builds_gesperrt_schutz_norm(self) -> None:
        feld = build_festkoerper_feld(feld_id="feld-341-stability")
        norm = next(n for n in feld.normen if n.geltung is FestkoerperGeltung.GESPERRT)

        self.assertIsInstance(feld, FestkoerperFeld)
        self.assertIsInstance(norm, FestkoerperNorm)
        self.assertEqual(norm.festkoerper_typ, FestkoerperTyp.SCHUTZ_FESTKOERPER)
        self.assertEqual(norm.prozedur, FestkoerperProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.festkoerper_tier, 1)

    def test_kki_festkoerper_feld_builds_festkoerperlich_ordnungs_norm(self) -> None:
        feld = build_festkoerper_feld(feld_id="feld-341-governance")
        norm = next(n for n in feld.normen if n.geltung is FestkoerperGeltung.FESTKOERPERLICH)

        self.assertEqual(norm.festkoerper_typ, FestkoerperTyp.ORDNUNGS_FESTKOERPER)
        self.assertEqual(norm.prozedur, FestkoerperProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.festkoerper_weight, 0.0)

    def test_kki_festkoerper_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        feld = build_festkoerper_feld(feld_id="feld-341-expansion")
        norm = next(n for n in feld.normen if n.geltung is FestkoerperGeltung.GRUNDLEGEND_FESTKOERPERLICH)

        self.assertEqual(norm.festkoerper_typ, FestkoerperTyp.SOUVERAENITAETS_FESTKOERPER)
        self.assertEqual(norm.prozedur, FestkoerperProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.festkoerper_weight, 0.0)

    def test_kki_festkoerper_feld_aggregates_feld_signal(self) -> None:
        feld = build_festkoerper_feld(feld_id="feld-341-signal")

        self.assertEqual(feld.feld_signal.status, "feld-gesperrt")
        self.assertEqual(feld.gesperrt_norm_ids, ("feld-341-signal-stability-lane",))
        self.assertEqual(feld.festkoerperlich_norm_ids, ("feld-341-signal-governance-lane",))
        self.assertEqual(feld.grundlegend_norm_ids, ("feld-341-signal-expansion-lane",))

    # #342 KristallgitterRegister
    def test_kki_kristallgitter_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_kristallgitter_register(register_id="register-342-stability")
        norm = next(n for n in register.normen if n.geltung is KristallgitterGeltung.GESPERRT)

        self.assertIsInstance(register, KristallgitterRegister)
        self.assertIsInstance(norm, KristallgitterNorm)
        self.assertEqual(norm.kristallgitter_typ, KristallgitterTyp.SCHUTZ_KRISTALLGITTER)
        self.assertEqual(norm.prozedur, KristallgitterProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kristallgitter_tier, 1)

    def test_kki_kristallgitter_register_builds_gittergeordnet_ordnungs_norm(self) -> None:
        register = build_kristallgitter_register(register_id="register-342-governance")
        norm = next(n for n in register.normen if n.geltung is KristallgitterGeltung.GITTERGEORDNET)

        self.assertEqual(norm.kristallgitter_typ, KristallgitterTyp.ORDNUNGS_KRISTALLGITTER)
        self.assertEqual(norm.prozedur, KristallgitterProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kristallgitter_weight, 0.0)

    def test_kki_kristallgitter_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_kristallgitter_register(register_id="register-342-expansion")
        norm = next(n for n in register.normen if n.geltung is KristallgitterGeltung.GRUNDLEGEND_GITTERGEORDNET)

        self.assertEqual(norm.kristallgitter_typ, KristallgitterTyp.SOUVERAENITAETS_KRISTALLGITTER)
        self.assertEqual(norm.prozedur, KristallgitterProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.kristallgitter_weight, 0.0)

    def test_kki_kristallgitter_register_aggregates_register_signal(self) -> None:
        register = build_kristallgitter_register(register_id="register-342-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-342-signal-stability-lane",))
        self.assertEqual(register.gittergeordnet_norm_ids, ("register-342-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-342-signal-expansion-lane",))

    # #343 BandstrukturCharta
    def test_kki_bandstruktur_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_bandstruktur_charta(charta_id="charta-343-stability")
        norm = next(n for n in charta.normen if n.geltung is BandstrukturGeltung.GESPERRT)

        self.assertIsInstance(charta, BandstrukturCharta)
        self.assertIsInstance(norm, BandstrukturNorm)
        self.assertEqual(norm.bandstruktur_typ, BandstrukturTyp.SCHUTZ_BANDSTRUKTUR)
        self.assertEqual(norm.prozedur, BandstrukturProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.bandstruktur_tier, 1)

    def test_kki_bandstruktur_charta_builds_bandstrukturiert_ordnungs_norm(self) -> None:
        charta = build_bandstruktur_charta(charta_id="charta-343-governance")
        norm = next(n for n in charta.normen if n.geltung is BandstrukturGeltung.BANDSTRUKTURIERT)

        self.assertEqual(norm.bandstruktur_typ, BandstrukturTyp.ORDNUNGS_BANDSTRUKTUR)
        self.assertEqual(norm.prozedur, BandstrukturProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.bandstruktur_weight, 0.0)

    def test_kki_bandstruktur_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_bandstruktur_charta(charta_id="charta-343-expansion")
        norm = next(n for n in charta.normen if n.geltung is BandstrukturGeltung.GRUNDLEGEND_BANDSTRUKTURIERT)

        self.assertEqual(norm.bandstruktur_typ, BandstrukturTyp.SOUVERAENITAETS_BANDSTRUKTUR)
        self.assertEqual(norm.prozedur, BandstrukturProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.bandstruktur_weight, 0.0)

    def test_kki_bandstruktur_charta_aggregates_charta_signal(self) -> None:
        charta = build_bandstruktur_charta(charta_id="charta-343-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-343-signal-stability-lane",))
        self.assertEqual(charta.bandstrukturiert_norm_ids, ("charta-343-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-343-signal-expansion-lane",))

    # #344 HalbleiterKodex
    def test_kki_halbleiter_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_halbleiter_kodex(kodex_id="kodex-344-stability")
        norm = next(n for n in kodex.normen if n.geltung is HalbleiterGeltung.GESPERRT)

        self.assertIsInstance(kodex, HalbleiterKodex)
        self.assertIsInstance(norm, HalbleiterNorm)
        self.assertEqual(norm.halbleiter_typ, HalbleiterTyp.SCHUTZ_HALBLEITER)
        self.assertEqual(norm.prozedur, HalbleiterProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.halbleiter_tier, 1)

    def test_kki_halbleiter_kodex_builds_halbleitend_ordnungs_norm(self) -> None:
        kodex = build_halbleiter_kodex(kodex_id="kodex-344-governance")
        norm = next(n for n in kodex.normen if n.geltung is HalbleiterGeltung.HALBLEITEND)

        self.assertEqual(norm.halbleiter_typ, HalbleiterTyp.ORDNUNGS_HALBLEITER)
        self.assertEqual(norm.prozedur, HalbleiterProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.halbleiter_weight, 0.0)

    def test_kki_halbleiter_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_halbleiter_kodex(kodex_id="kodex-344-expansion")
        norm = next(n for n in kodex.normen if n.geltung is HalbleiterGeltung.GRUNDLEGEND_HALBLEITEND)

        self.assertEqual(norm.halbleiter_typ, HalbleiterTyp.SOUVERAENITAETS_HALBLEITER)
        self.assertEqual(norm.prozedur, HalbleiterProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.halbleiter_weight, 0.0)

    def test_kki_halbleiter_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_halbleiter_kodex(kodex_id="kodex-344-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-344-signal-stability-lane",))
        self.assertEqual(kodex.halbleitend_norm_ids, ("kodex-344-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-344-signal-expansion-lane",))


    # #345 SupraleitungPakt
    def test_kki_supraleitung_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_supraleitung_pakt(pakt_id="pakt-345-stability")
        norm = next(n for n in pakt.normen if n.geltung is SupraleitungGeltung.GESPERRT)

        self.assertIsInstance(pakt, SupraleitungPakt)
        self.assertIsInstance(norm, SupraleitungNorm)
        self.assertEqual(norm.supraleitung_typ, SupraleitungTyp.SCHUTZ_SUPRALEITUNG)
        self.assertEqual(norm.prozedur, SupraleitungProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.supraleitung_tier, 1)

    def test_kki_supraleitung_pakt_builds_supraleitend_ordnungs_norm(self) -> None:
        pakt = build_supraleitung_pakt(pakt_id="pakt-345-governance")
        norm = next(n for n in pakt.normen if n.geltung is SupraleitungGeltung.SUPRALEITEND)

        self.assertEqual(norm.supraleitung_typ, SupraleitungTyp.ORDNUNGS_SUPRALEITUNG)
        self.assertEqual(norm.prozedur, SupraleitungProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.supraleitung_weight, 0.0)

    def test_kki_supraleitung_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_supraleitung_pakt(pakt_id="pakt-345-expansion")
        norm = next(n for n in pakt.normen if n.geltung is SupraleitungGeltung.GRUNDLEGEND_SUPRALEITEND)

        self.assertEqual(norm.supraleitung_typ, SupraleitungTyp.SOUVERAENITAETS_SUPRALEITUNG)
        self.assertEqual(norm.prozedur, SupraleitungProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.supraleitung_weight, 0.0)

    def test_kki_supraleitung_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_supraleitung_pakt(pakt_id="pakt-345-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-345-signal-stability-lane",))
        self.assertEqual(pakt.supraleitend_norm_ids, ("pakt-345-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-345-signal-expansion-lane",))

    # #346 QuantenHallManifest
    def test_kki_quanten_hall_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_quanten_hall_manifest(manifest_id="manifest-346-stability")
        norm = next(n for n in manifest.normen if n.geltung is QuantenHallGeltung.GESPERRT)

        self.assertIsInstance(manifest, QuantenHallManifest)
        self.assertIsInstance(norm, QuantenHallNorm)
        self.assertEqual(norm.quanten_hall_typ, QuantenHallTyp.SCHUTZ_QUANTEN_HALL)
        self.assertEqual(norm.prozedur, QuantenHallProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.quanten_hall_tier, 1)

    def test_kki_quanten_hall_manifest_builds_quantenhallisch_ordnungs_norm(self) -> None:
        manifest = build_quanten_hall_manifest(manifest_id="manifest-346-governance")
        norm = next(n for n in manifest.normen if n.geltung is QuantenHallGeltung.QUANTENHALLISCH)

        self.assertEqual(norm.quanten_hall_typ, QuantenHallTyp.ORDNUNGS_QUANTEN_HALL)
        self.assertEqual(norm.prozedur, QuantenHallProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.quanten_hall_weight, 0.0)

    def test_kki_quanten_hall_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_quanten_hall_manifest(manifest_id="manifest-346-expansion")
        norm = next(n for n in manifest.normen if n.geltung is QuantenHallGeltung.GRUNDLEGEND_QUANTENHALLISCH)

        self.assertEqual(norm.quanten_hall_typ, QuantenHallTyp.SOUVERAENITAETS_QUANTEN_HALL)
        self.assertEqual(norm.prozedur, QuantenHallProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.quanten_hall_weight, 0.0)

    def test_kki_quanten_hall_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_quanten_hall_manifest(manifest_id="manifest-346-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-346-signal-stability-lane",))
        self.assertEqual(manifest.quantenhallisch_norm_ids, ("manifest-346-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-346-signal-expansion-lane",))

    # #347 PhononSenat
    def test_kki_phonon_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_phonon_senat(senat_id="senat-347-stability")
        norm = next(n for n in senat.normen if n.geltung is PhononGeltung.GESPERRT)

        self.assertIsInstance(senat, PhononSenat)
        self.assertIsInstance(norm, PhononNorm)
        self.assertEqual(norm.phonon_typ, PhononTyp.SCHUTZ_PHONON)
        self.assertEqual(norm.prozedur, PhononProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.phonon_tier, 1)

    def test_kki_phonon_senat_builds_phononisch_ordnungs_norm(self) -> None:
        senat = build_phonon_senat(senat_id="senat-347-governance")
        norm = next(n for n in senat.normen if n.geltung is PhononGeltung.PHONONISCH)

        self.assertEqual(norm.phonon_typ, PhononTyp.ORDNUNGS_PHONON)
        self.assertEqual(norm.prozedur, PhononProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.phonon_weight, 0.0)

    def test_kki_phonon_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_phonon_senat(senat_id="senat-347-expansion")
        norm = next(n for n in senat.normen if n.geltung is PhononGeltung.GRUNDLEGEND_PHONONISCH)

        self.assertEqual(norm.phonon_typ, PhononTyp.SOUVERAENITAETS_PHONON)
        self.assertEqual(norm.prozedur, PhononProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.phonon_weight, 0.0)

    def test_kki_phonon_senat_aggregates_senat_signal(self) -> None:
        senat = build_phonon_senat(senat_id="senat-347-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-347-signal-stability-lane",))
        self.assertEqual(senat.phononisch_norm_ids, ("senat-347-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-347-signal-expansion-lane",))

    # #348 FermiNorm (*_norm)
    def test_kki_fermi_norm_builds_gesperrt_schutz_norm(self) -> None:
        satz = build_fermi_norm(norm_id="fermi-norm-348-stability")
        eintrag = next(n for n in satz.normen if n.geltung is FermiNormGeltung.GESPERRT)

        self.assertIsInstance(satz, FermiNormSatz)
        self.assertIsInstance(eintrag, FermiNormEintrag)
        self.assertEqual(eintrag.fermi_norm_typ, FermiNormTyp.SCHUTZ_FERMI_NORM)
        self.assertEqual(eintrag.prozedur, FermiNormProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.fermi_norm_tier, 1)

    def test_kki_fermi_norm_builds_ferminormiert_ordnungs_norm(self) -> None:
        satz = build_fermi_norm(norm_id="fermi-norm-348-governance")
        eintrag = next(n for n in satz.normen if n.geltung is FermiNormGeltung.FERMINORMIERT)

        self.assertEqual(eintrag.fermi_norm_typ, FermiNormTyp.ORDNUNGS_FERMI_NORM)
        self.assertEqual(eintrag.prozedur, FermiNormProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.fermi_norm_weight, 0.0)

    def test_kki_fermi_norm_builds_grundlegend_souveraenitaets_norm(self) -> None:
        satz = build_fermi_norm(norm_id="fermi-norm-348-expansion")
        eintrag = next(n for n in satz.normen if n.geltung is FermiNormGeltung.GRUNDLEGEND_FERMINORMIERT)

        self.assertEqual(eintrag.fermi_norm_typ, FermiNormTyp.SOUVERAENITAETS_FERMI_NORM)
        self.assertEqual(eintrag.prozedur, FermiNormProzedur.PLENARPROTOKOLL)
        self.assertGreater(eintrag.fermi_norm_weight, 0.0)

    def test_kki_fermi_norm_aggregates_norm_signal(self) -> None:
        satz = build_fermi_norm(norm_id="fermi-norm-348-signal")

        self.assertEqual(satz.norm_signal.status, "norm-gesperrt")
        self.assertEqual(satz.gesperrt_norm_ids, ("fermi-norm-348-signal-stability-lane",))
        self.assertEqual(satz.ferminormiert_norm_ids, ("fermi-norm-348-signal-governance-lane",))
        self.assertEqual(satz.grundlegend_norm_ids, ("fermi-norm-348-signal-expansion-lane",))


    # #349 BoseEinsteinCharta
    def test_kki_bose_einstein_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_bose_einstein_charta(charta_id="charta-349-stability")
        norm = next(n for n in charta.normen if n.geltung is BoseEinsteinGeltung.GESPERRT)

        self.assertIsInstance(charta, BoseEinsteinCharta)
        self.assertIsInstance(norm, BoseEinsteinNorm)
        self.assertEqual(norm.bose_einstein_typ, BoseEinsteinTyp.SCHUTZ_BOSE_EINSTEIN)
        self.assertEqual(norm.prozedur, BoseEinsteinProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.bose_einstein_tier, 1)

    def test_kki_bose_einstein_charta_builds_boseeinsteinkondensiert_ordnungs_norm(self) -> None:
        charta = build_bose_einstein_charta(charta_id="charta-349-governance")
        norm = next(n for n in charta.normen if n.geltung is BoseEinsteinGeltung.BOSEEINSTEINKONDENSIERT)

        self.assertEqual(norm.bose_einstein_typ, BoseEinsteinTyp.ORDNUNGS_BOSE_EINSTEIN)
        self.assertEqual(norm.prozedur, BoseEinsteinProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.bose_einstein_weight, 0.0)

    def test_kki_bose_einstein_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_bose_einstein_charta(charta_id="charta-349-expansion")
        norm = next(n for n in charta.normen if n.geltung is BoseEinsteinGeltung.GRUNDLEGEND_BOSEEINSTEINKONDENSIERT)

        self.assertEqual(norm.bose_einstein_typ, BoseEinsteinTyp.SOUVERAENITAETS_BOSE_EINSTEIN)
        self.assertEqual(norm.prozedur, BoseEinsteinProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.bose_einstein_weight, 0.0)

    def test_kki_bose_einstein_charta_aggregates_charta_signal(self) -> None:
        charta = build_bose_einstein_charta(charta_id="charta-349-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-349-signal-stability-lane",))
        self.assertEqual(charta.boseeinsteinkondensiert_norm_ids, ("charta-349-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-349-signal-expansion-lane",))

    # #350 FestkoerperVerfassung (Block-Krone)
    def test_kki_festkoerper_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_festkoerper_verfassung(verfassung_id="verfassung-350-stability")
        norm = next(n for n in verfassung.normen if n.geltung is FestkoerperVerfassungsGeltung.GESPERRT)

        self.assertIsInstance(verfassung, FestkoerperVerfassung)
        self.assertIsInstance(norm, FestkoerperVerfassungsNorm)
        self.assertEqual(norm.festkoerper_verfassungs_typ, FestkoerperVerfassungsTyp.SCHUTZ_FESTKOERPERVERFASSUNG)
        self.assertEqual(norm.prozedur, FestkoerperVerfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.festkoerper_verfassungs_tier, 1)

    def test_kki_festkoerper_verfassung_builds_festkoerperverfasst_ordnungs_norm(self) -> None:
        verfassung = build_festkoerper_verfassung(verfassung_id="verfassung-350-governance")
        norm = next(n for n in verfassung.normen if n.geltung is FestkoerperVerfassungsGeltung.FESTKOERPERVERFASST)

        self.assertEqual(norm.festkoerper_verfassungs_typ, FestkoerperVerfassungsTyp.ORDNUNGS_FESTKOERPERVERFASSUNG)
        self.assertEqual(norm.prozedur, FestkoerperVerfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.festkoerper_verfassungs_weight, 0.0)

    def test_kki_festkoerper_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_festkoerper_verfassung(verfassung_id="verfassung-350-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is FestkoerperVerfassungsGeltung.GRUNDLEGEND_FESTKOERPERVERFASST)

        self.assertEqual(norm.festkoerper_verfassungs_typ, FestkoerperVerfassungsTyp.SOUVERAENITAETS_FESTKOERPERVERFASSUNG)
        self.assertEqual(norm.prozedur, FestkoerperVerfassungsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.festkoerper_verfassungs_weight, 0.0)

    def test_kki_festkoerper_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_festkoerper_verfassung(verfassung_id="verfassung-350-signal")

        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-350-signal-stability-lane",))
        self.assertEqual(verfassung.festkoerperverfasst_norm_ids, ("verfassung-350-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-350-signal-expansion-lane",))


    # #351 PlasmaFeld
    def test_kki_plasma_feld_builds_gesperrt_schutz_norm(self) -> None:
        feld = build_plasma_feld(feld_id="feld-351-stability")
        norm = next(n for n in feld.normen if n.geltung is PlasmaGeltung.GESPERRT)

        self.assertIsInstance(feld, PlasmaFeld)
        self.assertIsInstance(norm, PlasmaNorm)
        self.assertEqual(norm.plasma_typ, PlasmaTyp.SCHUTZ_PLASMA)
        self.assertEqual(norm.prozedur, PlasmaProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.plasma_tier, 1)

    def test_kki_plasma_feld_builds_plasmatisch_ordnungs_norm(self) -> None:
        feld = build_plasma_feld(feld_id="feld-351-governance")
        norm = next(n for n in feld.normen if n.geltung is PlasmaGeltung.PLASMATISCH)

        self.assertEqual(norm.plasma_typ, PlasmaTyp.ORDNUNGS_PLASMA)
        self.assertEqual(norm.prozedur, PlasmaProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.plasma_weight, 0.0)

    def test_kki_plasma_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        feld = build_plasma_feld(feld_id="feld-351-expansion")
        norm = next(n for n in feld.normen if n.geltung is PlasmaGeltung.GRUNDLEGEND_PLASMATISCH)

        self.assertEqual(norm.plasma_typ, PlasmaTyp.SOUVERAENITAETS_PLASMA)
        self.assertEqual(norm.prozedur, PlasmaProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.plasma_weight, 0.0)

    def test_kki_plasma_feld_aggregates_feld_signal(self) -> None:
        feld = build_plasma_feld(feld_id="feld-351-signal")

        self.assertEqual(feld.feld_signal.status, "feld-gesperrt")
        self.assertEqual(feld.gesperrt_norm_ids, ("feld-351-signal-stability-lane",))
        self.assertEqual(feld.plasmatisch_norm_ids, ("feld-351-signal-governance-lane",))
        self.assertEqual(feld.grundlegend_norm_ids, ("feld-351-signal-expansion-lane",))

    # #352 MagnetohydrodynamikRegister
    def test_kki_magnetohydrodynamik_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_magnetohydrodynamik_register(register_id="register-352-stability")
        norm = next(n for n in register.normen if n.geltung is MagnetohydrodynamikGeltung.GESPERRT)

        self.assertIsInstance(register, MagnetohydrodynamikRegister)
        self.assertIsInstance(norm, MagnetohydrodynamikNorm)
        self.assertEqual(norm.magnetohydrodynamik_typ, MagnetohydrodynamikTyp.SCHUTZ_MAGNETOHYDRODYNAMIK)
        self.assertEqual(norm.prozedur, MagnetohydrodynamikProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.magnetohydrodynamik_tier, 1)

    def test_kki_magnetohydrodynamik_register_builds_magnetohydrodynamisch_ordnungs_norm(self) -> None:
        register = build_magnetohydrodynamik_register(register_id="register-352-governance")
        norm = next(n for n in register.normen if n.geltung is MagnetohydrodynamikGeltung.MAGNETOHYDRODYNAMISCH)

        self.assertEqual(norm.magnetohydrodynamik_typ, MagnetohydrodynamikTyp.ORDNUNGS_MAGNETOHYDRODYNAMIK)
        self.assertEqual(norm.prozedur, MagnetohydrodynamikProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.magnetohydrodynamik_weight, 0.0)

    def test_kki_magnetohydrodynamik_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_magnetohydrodynamik_register(register_id="register-352-expansion")
        norm = next(n for n in register.normen if n.geltung is MagnetohydrodynamikGeltung.GRUNDLEGEND_MAGNETOHYDRODYNAMISCH)

        self.assertEqual(norm.magnetohydrodynamik_typ, MagnetohydrodynamikTyp.SOUVERAENITAETS_MAGNETOHYDRODYNAMIK)
        self.assertEqual(norm.prozedur, MagnetohydrodynamikProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.magnetohydrodynamik_weight, 0.0)

    def test_kki_magnetohydrodynamik_register_aggregates_register_signal(self) -> None:
        register = build_magnetohydrodynamik_register(register_id="register-352-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-352-signal-stability-lane",))
        self.assertEqual(register.magnetohydrodynamisch_norm_ids, ("register-352-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-352-signal-expansion-lane",))

    # #353 DebyeAbschirmungCharta
    def test_kki_debye_abschirmung_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_debye_abschirmung_charta(charta_id="charta-353-stability")
        norm = next(n for n in charta.normen if n.geltung is DebyeAbschirmungGeltung.GESPERRT)

        self.assertIsInstance(charta, DebyeAbschirmungCharta)
        self.assertIsInstance(norm, DebyeAbschirmungNorm)
        self.assertEqual(norm.debye_abschirmung_typ, DebyeAbschirmungTyp.SCHUTZ_DEBYE_ABSCHIRMUNG)
        self.assertEqual(norm.prozedur, DebyeAbschirmungProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.debye_abschirmung_tier, 1)

    def test_kki_debye_abschirmung_charta_builds_debyeabgeschirmt_ordnungs_norm(self) -> None:
        charta = build_debye_abschirmung_charta(charta_id="charta-353-governance")
        norm = next(n for n in charta.normen if n.geltung is DebyeAbschirmungGeltung.DEBYEABGESCHIRMT)

        self.assertEqual(norm.debye_abschirmung_typ, DebyeAbschirmungTyp.ORDNUNGS_DEBYE_ABSCHIRMUNG)
        self.assertEqual(norm.prozedur, DebyeAbschirmungProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.debye_abschirmung_weight, 0.0)

    def test_kki_debye_abschirmung_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_debye_abschirmung_charta(charta_id="charta-353-expansion")
        norm = next(n for n in charta.normen if n.geltung is DebyeAbschirmungGeltung.GRUNDLEGEND_DEBYEABGESCHIRMT)

        self.assertEqual(norm.debye_abschirmung_typ, DebyeAbschirmungTyp.SOUVERAENITAETS_DEBYE_ABSCHIRMUNG)
        self.assertEqual(norm.prozedur, DebyeAbschirmungProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.debye_abschirmung_weight, 0.0)

    def test_kki_debye_abschirmung_charta_aggregates_charta_signal(self) -> None:
        charta = build_debye_abschirmung_charta(charta_id="charta-353-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-353-signal-stability-lane",))
        self.assertEqual(charta.debyeabgeschirmt_norm_ids, ("charta-353-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-353-signal-expansion-lane",))

    # #354 AlfvenWellenKodex
    def test_kki_alfven_wellen_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_alfven_wellen_kodex(kodex_id="kodex-354-stability")
        norm = next(n for n in kodex.normen if n.geltung is AlfvenWellenGeltung.GESPERRT)

        self.assertIsInstance(kodex, AlfvenWellenKodex)
        self.assertIsInstance(norm, AlfvenWellenNorm)
        self.assertEqual(norm.alfven_wellen_typ, AlfvenWellenTyp.SCHUTZ_ALFVEN_WELLEN)
        self.assertEqual(norm.prozedur, AlfvenWellenProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.alfven_wellen_tier, 1)

    def test_kki_alfven_wellen_kodex_builds_alfvenwellig_ordnungs_norm(self) -> None:
        kodex = build_alfven_wellen_kodex(kodex_id="kodex-354-governance")
        norm = next(n for n in kodex.normen if n.geltung is AlfvenWellenGeltung.ALFVENWELLIG)

        self.assertEqual(norm.alfven_wellen_typ, AlfvenWellenTyp.ORDNUNGS_ALFVEN_WELLEN)
        self.assertEqual(norm.prozedur, AlfvenWellenProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.alfven_wellen_weight, 0.0)

    def test_kki_alfven_wellen_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_alfven_wellen_kodex(kodex_id="kodex-354-expansion")
        norm = next(n for n in kodex.normen if n.geltung is AlfvenWellenGeltung.GRUNDLEGEND_ALFVENWELLIG)

        self.assertEqual(norm.alfven_wellen_typ, AlfvenWellenTyp.SOUVERAENITAETS_ALFVEN_WELLEN)
        self.assertEqual(norm.prozedur, AlfvenWellenProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.alfven_wellen_weight, 0.0)

    def test_kki_alfven_wellen_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_alfven_wellen_kodex(kodex_id="kodex-354-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-354-signal-stability-lane",))
        self.assertEqual(kodex.alfvenwellig_norm_ids, ("kodex-354-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-354-signal-expansion-lane",))


    # #355 ZPinchPakt
    def test_kki_z_pinch_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_z_pinch_pakt(pakt_id="pakt-355-stability")
        norm = next(n for n in pakt.normen if n.geltung is ZPinchGeltung.GESPERRT)

        self.assertIsInstance(pakt, ZPinchPakt)
        self.assertIsInstance(norm, ZPinchNorm)
        self.assertEqual(norm.z_pinch_typ, ZPinchTyp.SCHUTZ_Z_PINCH)
        self.assertEqual(norm.prozedur, ZPinchProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.z_pinch_tier, 1)

    def test_kki_z_pinch_pakt_builds_zpinchend_ordnungs_norm(self) -> None:
        pakt = build_z_pinch_pakt(pakt_id="pakt-355-governance")
        norm = next(n for n in pakt.normen if n.geltung is ZPinchGeltung.ZPINCHEND)

        self.assertEqual(norm.z_pinch_typ, ZPinchTyp.ORDNUNGS_Z_PINCH)
        self.assertEqual(norm.prozedur, ZPinchProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.z_pinch_weight, 0.0)

    def test_kki_z_pinch_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_z_pinch_pakt(pakt_id="pakt-355-expansion")
        norm = next(n for n in pakt.normen if n.geltung is ZPinchGeltung.GRUNDLEGEND_ZPINCHEND)

        self.assertEqual(norm.z_pinch_typ, ZPinchTyp.SOUVERAENITAETS_Z_PINCH)
        self.assertEqual(norm.prozedur, ZPinchProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.z_pinch_weight, 0.0)

    def test_kki_z_pinch_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_z_pinch_pakt(pakt_id="pakt-355-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-355-signal-stability-lane",))
        self.assertEqual(pakt.zpinchend_norm_ids, ("pakt-355-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-355-signal-expansion-lane",))

    # #356 TokamakManifest
    def test_kki_tokamak_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_tokamak_manifest(manifest_id="manifest-356-stability")
        norm = next(n for n in manifest.normen if n.geltung is TokamakGeltung.GESPERRT)

        self.assertIsInstance(manifest, TokamakManifest)
        self.assertIsInstance(norm, TokamakNorm)
        self.assertEqual(norm.tokamak_typ, TokamakTyp.SCHUTZ_TOKAMAK)
        self.assertEqual(norm.prozedur, TokamakProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.tokamak_tier, 1)

    def test_kki_tokamak_manifest_builds_tokamakisch_ordnungs_norm(self) -> None:
        manifest = build_tokamak_manifest(manifest_id="manifest-356-governance")
        norm = next(n for n in manifest.normen if n.geltung is TokamakGeltung.TOKAMAKISCH)

        self.assertEqual(norm.tokamak_typ, TokamakTyp.ORDNUNGS_TOKAMAK)
        self.assertEqual(norm.prozedur, TokamakProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.tokamak_weight, 0.0)

    def test_kki_tokamak_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_tokamak_manifest(manifest_id="manifest-356-expansion")
        norm = next(n for n in manifest.normen if n.geltung is TokamakGeltung.GRUNDLEGEND_TOKAMAKISCH)

        self.assertEqual(norm.tokamak_typ, TokamakTyp.SOUVERAENITAETS_TOKAMAK)
        self.assertEqual(norm.prozedur, TokamakProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.tokamak_weight, 0.0)

    def test_kki_tokamak_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_tokamak_manifest(manifest_id="manifest-356-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-356-signal-stability-lane",))
        self.assertEqual(manifest.tokamakisch_norm_ids, ("manifest-356-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-356-signal-expansion-lane",))

    # #357 TraegheitsfusionSenat
    def test_kki_traegheitsfusion_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_traegheitsfusion_senat(senat_id="senat-357-stability")
        norm = next(n for n in senat.normen if n.geltung is TraegheitsfusionGeltung.GESPERRT)

        self.assertIsInstance(senat, TraegheitsfusionSenat)
        self.assertIsInstance(norm, TraegheitsfusionNorm)
        self.assertEqual(norm.traegheitsfusion_typ, TraegheitsfusionTyp.SCHUTZ_TRAEGHEITSFUSION)
        self.assertEqual(norm.prozedur, TraegheitsfusionProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.traegheitsfusion_tier, 1)

    def test_kki_traegheitsfusion_senat_builds_traegheitsfusionierend_ordnungs_norm(self) -> None:
        senat = build_traegheitsfusion_senat(senat_id="senat-357-governance")
        norm = next(n for n in senat.normen if n.geltung is TraegheitsfusionGeltung.TRAEGHEITSFUSIONIEREND)

        self.assertEqual(norm.traegheitsfusion_typ, TraegheitsfusionTyp.ORDNUNGS_TRAEGHEITSFUSION)
        self.assertEqual(norm.prozedur, TraegheitsfusionProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.traegheitsfusion_weight, 0.0)

    def test_kki_traegheitsfusion_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_traegheitsfusion_senat(senat_id="senat-357-expansion")
        norm = next(n for n in senat.normen if n.geltung is TraegheitsfusionGeltung.GRUNDLEGEND_TRAEGHEITSFUSIONIEREND)

        self.assertEqual(norm.traegheitsfusion_typ, TraegheitsfusionTyp.SOUVERAENITAETS_TRAEGHEITSFUSION)
        self.assertEqual(norm.prozedur, TraegheitsfusionProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.traegheitsfusion_weight, 0.0)

    def test_kki_traegheitsfusion_senat_aggregates_senat_signal(self) -> None:
        senat = build_traegheitsfusion_senat(senat_id="senat-357-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-357-signal-stability-lane",))
        self.assertEqual(senat.traegheitsfusionierend_norm_ids, ("senat-357-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-357-signal-expansion-lane",))

    # #358 PlasmaWellenNorm (*_norm)
    def test_kki_plasmawellen_norm_builds_gesperrt_schutz_norm(self) -> None:
        normsatz = build_plasmawellen_norm(norm_id="plasmawellen-norm-358-stability")
        eintrag = next(n for n in normsatz.normen if n.geltung is PlasmaWellenNormGeltung.GESPERRT)

        self.assertIsInstance(normsatz, PlasmaWellenNormSatz)
        self.assertIsInstance(eintrag, PlasmaWellenNormEintrag)
        self.assertEqual(eintrag.plasmawellen_norm_typ, PlasmaWellenNormTyp.SCHUTZ_PLASMAWELLEN_NORM)
        self.assertEqual(eintrag.prozedur, PlasmaWellenNormProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.plasmawellen_norm_tier, 1)

    def test_kki_plasmawellen_norm_builds_plasmawellig_ordnungs_norm(self) -> None:
        normsatz = build_plasmawellen_norm(norm_id="plasmawellen-norm-358-governance")
        eintrag = next(n for n in normsatz.normen if n.geltung is PlasmaWellenNormGeltung.PLASMAWELLIG)

        self.assertEqual(eintrag.plasmawellen_norm_typ, PlasmaWellenNormTyp.ORDNUNGS_PLASMAWELLEN_NORM)
        self.assertEqual(eintrag.prozedur, PlasmaWellenNormProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.plasmawellen_norm_weight, 0.0)

    def test_kki_plasmawellen_norm_builds_grundlegend_souveraenitaets_norm(self) -> None:
        normsatz = build_plasmawellen_norm(norm_id="plasmawellen-norm-358-expansion")
        eintrag = next(n for n in normsatz.normen if n.geltung is PlasmaWellenNormGeltung.GRUNDLEGEND_PLASMAWELLIG)

        self.assertEqual(eintrag.plasmawellen_norm_typ, PlasmaWellenNormTyp.SOUVERAENITAETS_PLASMAWELLEN_NORM)
        self.assertEqual(eintrag.prozedur, PlasmaWellenNormProzedur.PLENARPROTOKOLL)
        self.assertGreater(eintrag.plasmawellen_norm_weight, 0.0)

    def test_kki_plasmawellen_norm_aggregates_norm_signal(self) -> None:
        normsatz = build_plasmawellen_norm(norm_id="plasmawellen-norm-358-signal")

        self.assertEqual(normsatz.norm_signal.status, "norm-gesperrt")
        self.assertEqual(normsatz.gesperrt_norm_ids, ("plasmawellen-norm-358-signal-stability-lane",))
        self.assertEqual(normsatz.plasmawellig_norm_ids, ("plasmawellen-norm-358-signal-governance-lane",))
        self.assertEqual(normsatz.grundlegend_norm_ids, ("plasmawellen-norm-358-signal-expansion-lane",))


    # #359 KernfusionCharta
    def test_kki_kernfusion_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_kernfusion_charta(charta_id="charta-359-stability")
        norm = next(n for n in charta.normen if n.geltung is KernfusionGeltung.GESPERRT)

        self.assertIsInstance(charta, KernfusionCharta)
        self.assertIsInstance(norm, KernfusionNorm)
        self.assertEqual(norm.kernfusion_typ, KernfusionTyp.SCHUTZ_KERNFUSION)
        self.assertEqual(norm.prozedur, KernfusionProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kernfusion_tier, 1)

    def test_kki_kernfusion_charta_builds_kernfusionierend_ordnungs_norm(self) -> None:
        charta = build_kernfusion_charta(charta_id="charta-359-governance")
        norm = next(n for n in charta.normen if n.geltung is KernfusionGeltung.KERNFUSIONIEREND)

        self.assertEqual(norm.kernfusion_typ, KernfusionTyp.ORDNUNGS_KERNFUSION)
        self.assertEqual(norm.prozedur, KernfusionProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kernfusion_weight, 0.0)

    def test_kki_kernfusion_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_kernfusion_charta(charta_id="charta-359-expansion")
        norm = next(n for n in charta.normen if n.geltung is KernfusionGeltung.GRUNDLEGEND_KERNFUSIONIEREND)

        self.assertEqual(norm.kernfusion_typ, KernfusionTyp.SOUVERAENITAETS_KERNFUSION)
        self.assertEqual(norm.prozedur, KernfusionProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.kernfusion_weight, 0.0)

    def test_kki_kernfusion_charta_aggregates_charta_signal(self) -> None:
        charta = build_kernfusion_charta(charta_id="charta-359-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-359-signal-stability-lane",))
        self.assertEqual(charta.kernfusionierend_norm_ids, ("charta-359-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-359-signal-expansion-lane",))

    # #360 PlasmaVerfassung (Block-Krone)
    def test_kki_plasma_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_plasma_verfassung(verfassung_id="verfassung-360-stability")
        norm = next(n for n in verfassung.normen if n.geltung is PlasmaVerfassungsGeltung.GESPERRT)

        self.assertIsInstance(verfassung, PlasmaVerfassung)
        self.assertIsInstance(norm, PlasmaVerfassungsNorm)
        self.assertEqual(norm.plasma_verfassungs_typ, PlasmaVerfassungsTyp.SCHUTZ_PLASMAVERFASSUNG)
        self.assertEqual(norm.prozedur, PlasmaVerfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.plasma_verfassungs_tier, 1)

    def test_kki_plasma_verfassung_builds_plasmaverfasst_ordnungs_norm(self) -> None:
        verfassung = build_plasma_verfassung(verfassung_id="verfassung-360-governance")
        norm = next(n for n in verfassung.normen if n.geltung is PlasmaVerfassungsGeltung.PLASMAVERFASST)

        self.assertEqual(norm.plasma_verfassungs_typ, PlasmaVerfassungsTyp.ORDNUNGS_PLASMAVERFASSUNG)
        self.assertEqual(norm.prozedur, PlasmaVerfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.plasma_verfassungs_weight, 0.0)

    def test_kki_plasma_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_plasma_verfassung(verfassung_id="verfassung-360-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is PlasmaVerfassungsGeltung.GRUNDLEGEND_PLASMAVERFASST)

        self.assertEqual(norm.plasma_verfassungs_typ, PlasmaVerfassungsTyp.SOUVERAENITAETS_PLASMAVERFASSUNG)
        self.assertEqual(norm.prozedur, PlasmaVerfassungsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.plasma_verfassungs_weight, 0.0)

    def test_kki_plasma_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_plasma_verfassung(verfassung_id="verfassung-360-signal")

        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-360-signal-stability-lane",))
        self.assertEqual(verfassung.plasmaverfasst_norm_ids, ("verfassung-360-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-360-signal-expansion-lane",))


    # #361 LorenzAttraktorFeld
    def test_kki_lorenz_attraktor_feld_builds_gesperrt_schutz_norm(self) -> None:
        feld = build_lorenz_attraktor_feld(feld_id="feld-361-stability")
        norm = next(n for n in feld.normen if n.geltung is LorenzAttraktorGeltung.GESPERRT)

        self.assertIsInstance(feld, LorenzAttraktorFeld)
        self.assertIsInstance(norm, LorenzAttraktorNorm)
        self.assertEqual(norm.lorenz_attraktor_typ, LorenzAttraktorTyp.SCHUTZ_LORENZ_ATTRAKTOR)
        self.assertEqual(norm.prozedur, LorenzAttraktorProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.lorenz_attraktor_tier, 1)

    def test_kki_lorenz_attraktor_feld_builds_lorenzattrahiert_ordnungs_norm(self) -> None:
        feld = build_lorenz_attraktor_feld(feld_id="feld-361-governance")
        norm = next(n for n in feld.normen if n.geltung is LorenzAttraktorGeltung.LORENZATTRAHIERT)

        self.assertEqual(norm.lorenz_attraktor_typ, LorenzAttraktorTyp.ORDNUNGS_LORENZ_ATTRAKTOR)
        self.assertEqual(norm.prozedur, LorenzAttraktorProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.lorenz_attraktor_weight, 0.0)

    def test_kki_lorenz_attraktor_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        feld = build_lorenz_attraktor_feld(feld_id="feld-361-expansion")
        norm = next(n for n in feld.normen if n.geltung is LorenzAttraktorGeltung.GRUNDLEGEND_LORENZATTRAHIERT)

        self.assertEqual(norm.lorenz_attraktor_typ, LorenzAttraktorTyp.SOUVERAENITAETS_LORENZ_ATTRAKTOR)
        self.assertEqual(norm.prozedur, LorenzAttraktorProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.lorenz_attraktor_weight, 0.0)

    def test_kki_lorenz_attraktor_feld_aggregates_feld_signal(self) -> None:
        feld = build_lorenz_attraktor_feld(feld_id="feld-361-signal")

        self.assertEqual(feld.feld_signal.status, "feld-gesperrt")
        self.assertEqual(feld.gesperrt_norm_ids, ("feld-361-signal-stability-lane",))
        self.assertEqual(feld.lorenzattrahiert_norm_ids, ("feld-361-signal-governance-lane",))
        self.assertEqual(feld.grundlegend_norm_ids, ("feld-361-signal-expansion-lane",))

    # #362 BifurkationsRegister
    def test_kki_bifurkations_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_bifurkations_register(register_id="register-362-stability")
        norm = next(n for n in register.normen if n.geltung is BifurkationsGeltung.GESPERRT)

        self.assertIsInstance(register, BifurkationsRegister)
        self.assertIsInstance(norm, BifurkationsNorm)
        self.assertEqual(norm.bifurkations_typ, BifurkationsTyp.SCHUTZ_BIFURKATION)
        self.assertEqual(norm.prozedur, BifurkationsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.bifurkations_tier, 1)

    def test_kki_bifurkations_register_builds_bifurkiert_ordnungs_norm(self) -> None:
        register = build_bifurkations_register(register_id="register-362-governance")
        norm = next(n for n in register.normen if n.geltung is BifurkationsGeltung.BIFURKIERT)

        self.assertEqual(norm.bifurkations_typ, BifurkationsTyp.ORDNUNGS_BIFURKATION)
        self.assertEqual(norm.prozedur, BifurkationsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.bifurkations_weight, 0.0)

    def test_kki_bifurkations_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_bifurkations_register(register_id="register-362-expansion")
        norm = next(n for n in register.normen if n.geltung is BifurkationsGeltung.GRUNDLEGEND_BIFURKIERT)

        self.assertEqual(norm.bifurkations_typ, BifurkationsTyp.SOUVERAENITAETS_BIFURKATION)
        self.assertEqual(norm.prozedur, BifurkationsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.bifurkations_weight, 0.0)

    def test_kki_bifurkations_register_aggregates_register_signal(self) -> None:
        register = build_bifurkations_register(register_id="register-362-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-362-signal-stability-lane",))
        self.assertEqual(register.bifurkiert_norm_ids, ("register-362-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-362-signal-expansion-lane",))

    # #363 LyapunovKodex
    def test_kki_lyapunov_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_lyapunov_kodex(kodex_id="kodex-363-stability")
        norm = next(n for n in kodex.normen if n.geltung is LyapunovGeltung.GESPERRT)

        self.assertIsInstance(kodex, LyapunovKodex)
        self.assertIsInstance(norm, LyapunovNorm)
        self.assertEqual(norm.lyapunov_typ, LyapunovTyp.SCHUTZ_LYAPUNOV)
        self.assertEqual(norm.prozedur, LyapunovProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.lyapunov_tier, 1)

    def test_kki_lyapunov_kodex_builds_lyapunovstabil_ordnungs_norm(self) -> None:
        kodex = build_lyapunov_kodex(kodex_id="kodex-363-governance")
        norm = next(n for n in kodex.normen if n.geltung is LyapunovGeltung.LYAPUNOVSTABIL)

        self.assertEqual(norm.lyapunov_typ, LyapunovTyp.ORDNUNGS_LYAPUNOV)
        self.assertEqual(norm.prozedur, LyapunovProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.lyapunov_weight, 0.0)

    def test_kki_lyapunov_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_lyapunov_kodex(kodex_id="kodex-363-expansion")
        norm = next(n for n in kodex.normen if n.geltung is LyapunovGeltung.GRUNDLEGEND_LYAPUNOVSTABIL)

        self.assertEqual(norm.lyapunov_typ, LyapunovTyp.SOUVERAENITAETS_LYAPUNOV)
        self.assertEqual(norm.prozedur, LyapunovProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.lyapunov_weight, 0.0)

    def test_kki_lyapunov_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_lyapunov_kodex(kodex_id="kodex-363-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-363-signal-stability-lane",))
        self.assertEqual(kodex.lyapunovstabil_norm_ids, ("kodex-363-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-363-signal-expansion-lane",))

    # #364 FraktalCharta
    def test_kki_fraktal_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_fraktal_charta(charta_id="charta-364-stability")
        norm = next(n for n in charta.normen if n.geltung is FraktalGeltung.GESPERRT)

        self.assertIsInstance(charta, FraktalCharta)
        self.assertIsInstance(norm, FraktalNorm)
        self.assertEqual(norm.fraktal_typ, FraktalTyp.SCHUTZ_FRAKTAL)
        self.assertEqual(norm.prozedur, FraktalProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.fraktal_tier, 1)

    def test_kki_fraktal_charta_builds_fraktal_ordnungs_norm(self) -> None:
        charta = build_fraktal_charta(charta_id="charta-364-governance")
        norm = next(n for n in charta.normen if n.geltung is FraktalGeltung.FRAKTAL)

        self.assertEqual(norm.fraktal_typ, FraktalTyp.ORDNUNGS_FRAKTAL)
        self.assertEqual(norm.prozedur, FraktalProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.fraktal_weight, 0.0)

    def test_kki_fraktal_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_fraktal_charta(charta_id="charta-364-expansion")
        norm = next(n for n in charta.normen if n.geltung is FraktalGeltung.GRUNDLEGEND_FRAKTAL)

        self.assertEqual(norm.fraktal_typ, FraktalTyp.SOUVERAENITAETS_FRAKTAL)
        self.assertEqual(norm.prozedur, FraktalProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.fraktal_weight, 0.0)

    def test_kki_fraktal_charta_aggregates_charta_signal(self) -> None:
        charta = build_fraktal_charta(charta_id="charta-364-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-364-signal-stability-lane",))
        self.assertEqual(charta.fraktal_norm_ids, ("charta-364-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-364-signal-expansion-lane",))


    # #365 StrangeAttraktorPakt
    def test_kki_strange_attraktor_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_strange_attraktor_pakt(pakt_id="pakt-365-stability")
        norm = next(n for n in pakt.normen if n.geltung is StrangeAttraktorGeltung.GESPERRT)

        self.assertIsInstance(pakt, StrangeAttraktorPakt)
        self.assertIsInstance(norm, StrangeAttraktorNorm)
        self.assertEqual(norm.strange_attraktor_typ, StrangeAttraktorTyp.SCHUTZ_STRANGE_ATTRAKTOR)
        self.assertEqual(norm.prozedur, StrangeAttraktorProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.strange_attraktor_tier, 1)

    def test_kki_strange_attraktor_pakt_builds_strangeattrahiert_ordnungs_norm(self) -> None:
        pakt = build_strange_attraktor_pakt(pakt_id="pakt-365-governance")
        norm = next(n for n in pakt.normen if n.geltung is StrangeAttraktorGeltung.STRANGEATTRAHIERT)

        self.assertEqual(norm.strange_attraktor_typ, StrangeAttraktorTyp.ORDNUNGS_STRANGE_ATTRAKTOR)
        self.assertEqual(norm.prozedur, StrangeAttraktorProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.strange_attraktor_weight, 0.0)

    def test_kki_strange_attraktor_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_strange_attraktor_pakt(pakt_id="pakt-365-expansion")
        norm = next(n for n in pakt.normen if n.geltung is StrangeAttraktorGeltung.GRUNDLEGEND_STRANGEATTRAHIERT)

        self.assertEqual(norm.strange_attraktor_typ, StrangeAttraktorTyp.SOUVERAENITAETS_STRANGE_ATTRAKTOR)
        self.assertEqual(norm.prozedur, StrangeAttraktorProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.strange_attraktor_weight, 0.0)

    def test_kki_strange_attraktor_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_strange_attraktor_pakt(pakt_id="pakt-365-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-365-signal-stability-lane",))
        self.assertEqual(pakt.strangeattrahiert_norm_ids, ("pakt-365-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-365-signal-expansion-lane",))

    # #366 EmergenzSenat
    def test_kki_emergenz_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_emergenz_senat(senat_id="senat-366-stability")
        norm = next(n for n in senat.normen if n.geltung is EmergenzGeltung.GESPERRT)

        self.assertIsInstance(senat, EmergenzSenat)
        self.assertIsInstance(norm, EmergenzNorm)
        self.assertEqual(norm.emergenz_typ, EmergenzTyp.SCHUTZ_EMERGENZ)
        self.assertEqual(norm.prozedur, EmergenzProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.emergenz_tier, 1)

    def test_kki_emergenz_senat_builds_emergent_ordnungs_norm(self) -> None:
        senat = build_emergenz_senat(senat_id="senat-366-governance")
        norm = next(n for n in senat.normen if n.geltung is EmergenzGeltung.EMERGENT)

        self.assertEqual(norm.emergenz_typ, EmergenzTyp.ORDNUNGS_EMERGENZ)
        self.assertEqual(norm.prozedur, EmergenzProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.emergenz_weight, 0.0)

    def test_kki_emergenz_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_emergenz_senat(senat_id="senat-366-expansion")
        norm = next(n for n in senat.normen if n.geltung is EmergenzGeltung.GRUNDLEGEND_EMERGENT)

        self.assertEqual(norm.emergenz_typ, EmergenzTyp.SOUVERAENITAETS_EMERGENZ)
        self.assertEqual(norm.prozedur, EmergenzProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.emergenz_weight, 0.0)

    def test_kki_emergenz_senat_aggregates_senat_signal(self) -> None:
        senat = build_emergenz_senat(senat_id="senat-366-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-366-signal-stability-lane",))
        self.assertEqual(senat.emergent_norm_ids, ("senat-366-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-366-signal-expansion-lane",))

    # #367 PerkolationsNorm
    def test_kki_perkolations_norm_builds_gesperrt_schutz_norm(self) -> None:
        satz = build_perkolations_norm(norm_id="norm-367-stability")
        norm = next(n for n in satz.normen if n.geltung is PerkolationsNormGeltung.GESPERRT)

        self.assertIsInstance(satz, PerkolationsNormSatz)
        self.assertIsInstance(norm, PerkolationsNormEintrag)
        self.assertEqual(norm.perkolations_norm_typ, PerkolationsNormTyp.SCHUTZ_PERKOLATIONS_NORM)
        self.assertEqual(norm.prozedur, PerkolationsNormProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.perkolations_norm_tier, 1)

    def test_kki_perkolations_norm_builds_perkolierend_ordnungs_norm(self) -> None:
        satz = build_perkolations_norm(norm_id="norm-367-governance")
        norm = next(n for n in satz.normen if n.geltung is PerkolationsNormGeltung.PERKOLIEREND)

        self.assertEqual(norm.perkolations_norm_typ, PerkolationsNormTyp.ORDNUNGS_PERKOLATIONS_NORM)
        self.assertEqual(norm.prozedur, PerkolationsNormProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.perkolations_norm_weight, 0.0)

    def test_kki_perkolations_norm_builds_grundlegend_souveraenitaets_norm(self) -> None:
        satz = build_perkolations_norm(norm_id="norm-367-expansion")
        norm = next(n for n in satz.normen if n.geltung is PerkolationsNormGeltung.GRUNDLEGEND_PERKOLIEREND)

        self.assertEqual(norm.perkolations_norm_typ, PerkolationsNormTyp.SOUVERAENITAETS_PERKOLATIONS_NORM)
        self.assertEqual(norm.prozedur, PerkolationsNormProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.perkolations_norm_weight, 0.0)

    def test_kki_perkolations_norm_aggregates_norm_signal(self) -> None:
        satz = build_perkolations_norm(norm_id="norm-367-signal")

        self.assertEqual(satz.norm_signal.status, "norm-gesperrt")
        self.assertEqual(satz.gesperrt_norm_ids, ("norm-367-signal-stability-lane",))
        self.assertEqual(satz.perkolierend_norm_ids, ("norm-367-signal-governance-lane",))
        self.assertEqual(satz.grundlegend_norm_ids, ("norm-367-signal-expansion-lane",))

    # #368 KomplexitaetsCharta
    def test_kki_komplexitaets_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_komplexitaets_charta(charta_id="charta-368-stability")
        norm = next(n for n in charta.normen if n.geltung is KomplexitaetsGeltung.GESPERRT)

        self.assertIsInstance(charta, KomplexitaetsCharta)
        self.assertIsInstance(norm, KomplexitaetsNorm)
        self.assertEqual(norm.komplexitaets_typ, KomplexitaetsTyp.SCHUTZ_KOMPLEXITAET)
        self.assertEqual(norm.prozedur, KomplexitaetsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.komplexitaets_tier, 1)

    def test_kki_komplexitaets_charta_builds_komplexitaetsbewertet_ordnungs_norm(self) -> None:
        charta = build_komplexitaets_charta(charta_id="charta-368-governance")
        norm = next(n for n in charta.normen if n.geltung is KomplexitaetsGeltung.KOMPLEXITAETSBEWERTET)

        self.assertEqual(norm.komplexitaets_typ, KomplexitaetsTyp.ORDNUNGS_KOMPLEXITAET)
        self.assertEqual(norm.prozedur, KomplexitaetsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.komplexitaets_weight, 0.0)

    def test_kki_komplexitaets_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_komplexitaets_charta(charta_id="charta-368-expansion")
        norm = next(n for n in charta.normen if n.geltung is KomplexitaetsGeltung.GRUNDLEGEND_KOMPLEXITAETSBEWERTET)

        self.assertEqual(norm.komplexitaets_typ, KomplexitaetsTyp.SOUVERAENITAETS_KOMPLEXITAET)
        self.assertEqual(norm.prozedur, KomplexitaetsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.komplexitaets_weight, 0.0)

    def test_kki_komplexitaets_charta_aggregates_charta_signal(self) -> None:
        charta = build_komplexitaets_charta(charta_id="charta-368-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-368-signal-stability-lane",))
        self.assertEqual(charta.komplexitaetsbewertet_norm_ids, ("charta-368-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-368-signal-expansion-lane",))


    # #369 AdaptivSchwarmKodex
    def test_kki_adaptiv_schwarm_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_adaptiv_schwarm_kodex(kodex_id="kodex-369-stability")
        norm = next(n for n in kodex.normen if n.geltung is AdaptivSchwarmGeltung.GESPERRT)

        self.assertIsInstance(kodex, AdaptivSchwarmKodex)
        self.assertIsInstance(norm, AdaptivSchwarmNorm)
        self.assertEqual(norm.adaptiv_schwarm_typ, AdaptivSchwarmTyp.SCHUTZ_ADAPTIV_SCHWARM)
        self.assertEqual(norm.prozedur, AdaptivSchwarmProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.adaptiv_schwarm_tier, 1)

    def test_kki_adaptiv_schwarm_kodex_builds_adaptivschwarmend_ordnungs_norm(self) -> None:
        kodex = build_adaptiv_schwarm_kodex(kodex_id="kodex-369-governance")
        norm = next(n for n in kodex.normen if n.geltung is AdaptivSchwarmGeltung.ADAPTIV_SCHWARMEND)

        self.assertEqual(norm.adaptiv_schwarm_typ, AdaptivSchwarmTyp.ORDNUNGS_ADAPTIV_SCHWARM)
        self.assertEqual(norm.prozedur, AdaptivSchwarmProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.adaptiv_schwarm_weight, 0.0)

    def test_kki_adaptiv_schwarm_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_adaptiv_schwarm_kodex(kodex_id="kodex-369-expansion")
        norm = next(n for n in kodex.normen if n.geltung is AdaptivSchwarmGeltung.GRUNDLEGEND_ADAPTIV_SCHWARMEND)

        self.assertEqual(norm.adaptiv_schwarm_typ, AdaptivSchwarmTyp.SOUVERAENITAETS_ADAPTIV_SCHWARM)
        self.assertEqual(norm.prozedur, AdaptivSchwarmProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.adaptiv_schwarm_weight, 0.0)

    def test_kki_adaptiv_schwarm_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_adaptiv_schwarm_kodex(kodex_id="kodex-369-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-369-signal-stability-lane",))
        self.assertEqual(kodex.adaptivschwarmend_norm_ids, ("kodex-369-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-369-signal-expansion-lane",))

    # #370 ChaosVerfassung (Block-Krone)
    def test_kki_chaos_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_chaos_verfassung(verfassung_id="verfassung-370-stability")
        norm = next(n for n in verfassung.normen if n.geltung is ChaosVerfassungsGeltung.GESPERRT)

        self.assertIsInstance(verfassung, ChaosVerfassung)
        self.assertIsInstance(norm, ChaosVerfassungsNorm)
        self.assertEqual(norm.chaos_verfassungs_typ, ChaosVerfassungsTyp.SCHUTZ_CHAOSVERFASSUNG)
        self.assertEqual(norm.prozedur, ChaosVerfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.chaos_verfassungs_tier, 1)

    def test_kki_chaos_verfassung_builds_chaosverfasst_ordnungs_norm(self) -> None:
        verfassung = build_chaos_verfassung(verfassung_id="verfassung-370-governance")
        norm = next(n for n in verfassung.normen if n.geltung is ChaosVerfassungsGeltung.CHAOSVERFASST)

        self.assertEqual(norm.chaos_verfassungs_typ, ChaosVerfassungsTyp.ORDNUNGS_CHAOSVERFASSUNG)
        self.assertEqual(norm.prozedur, ChaosVerfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.chaos_verfassungs_weight, 0.0)

    def test_kki_chaos_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_chaos_verfassung(verfassung_id="verfassung-370-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is ChaosVerfassungsGeltung.GRUNDLEGEND_CHAOSVERFASST)

        self.assertEqual(norm.chaos_verfassungs_typ, ChaosVerfassungsTyp.SOUVERAENITAETS_CHAOSVERFASSUNG)
        self.assertEqual(norm.prozedur, ChaosVerfassungsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.chaos_verfassungs_weight, 0.0)

    def test_kki_chaos_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_chaos_verfassung(verfassung_id="verfassung-370-signal")

        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-370-signal-stability-lane",))
        self.assertEqual(verfassung.chaosverfasst_norm_ids, ("verfassung-370-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-370-signal-expansion-lane",))


    # #371 ShannonEntropieFeld
    def test_kki_shannon_entropie_feld_builds_gesperrt_schutz_norm(self) -> None:
        feld = build_shannon_entropie_feld(feld_id="feld-371-stability")
        norm = next(n for n in feld.normen if n.geltung is ShannonEntropieGeltung.GESPERRT)

        self.assertIsInstance(feld, ShannonEntropieFeld)
        self.assertIsInstance(norm, ShannonEntropieNorm)
        self.assertEqual(norm.shannon_entropie_typ, ShannonEntropieTyp.SCHUTZ_SHANNON_ENTROPIE)
        self.assertEqual(norm.prozedur, ShannonEntropieProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.shannon_entropie_tier, 1)

    def test_kki_shannon_entropie_feld_builds_entropisch_ordnungs_norm(self) -> None:
        feld = build_shannon_entropie_feld(feld_id="feld-371-governance")
        norm = next(n for n in feld.normen if n.geltung is ShannonEntropieGeltung.ENTROPISCH)

        self.assertEqual(norm.shannon_entropie_typ, ShannonEntropieTyp.ORDNUNGS_SHANNON_ENTROPIE)
        self.assertEqual(norm.prozedur, ShannonEntropieProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.shannon_entropie_weight, 0.0)

    def test_kki_shannon_entropie_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        feld = build_shannon_entropie_feld(feld_id="feld-371-expansion")
        norm = next(n for n in feld.normen if n.geltung is ShannonEntropieGeltung.GRUNDLEGEND_ENTROPISCH)

        self.assertEqual(norm.shannon_entropie_typ, ShannonEntropieTyp.SOUVERAENITAETS_SHANNON_ENTROPIE)
        self.assertEqual(norm.prozedur, ShannonEntropieProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.shannon_entropie_weight, 0.0)

    def test_kki_shannon_entropie_feld_aggregates_feld_signal(self) -> None:
        feld = build_shannon_entropie_feld(feld_id="feld-371-signal")

        self.assertEqual(feld.feld_signal.status, "feld-gesperrt")
        self.assertEqual(feld.gesperrt_norm_ids, ("feld-371-signal-stability-lane",))
        self.assertEqual(feld.entropisch_norm_ids, ("feld-371-signal-governance-lane",))
        self.assertEqual(feld.grundlegend_norm_ids, ("feld-371-signal-expansion-lane",))

    # #372 KanalkapazitaetRegister
    def test_kki_kanalkapazitaet_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_kanalkapazitaet_register(register_id="register-372-stability")
        norm = next(n for n in register.normen if n.geltung is KanalkapazitaetGeltung.GESPERRT)

        self.assertIsInstance(register, KanalkapazitaetRegister)
        self.assertIsInstance(norm, KanalkapazitaetNorm)
        self.assertEqual(norm.kanalkapazitaet_typ, KanalkapazitaetTyp.SCHUTZ_KANALKAPAZITAET)
        self.assertEqual(norm.prozedur, KanalkapazitaetProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kanalkapazitaet_tier, 1)

    def test_kki_kanalkapazitaet_register_builds_kapazitiv_ordnungs_norm(self) -> None:
        register = build_kanalkapazitaet_register(register_id="register-372-governance")
        norm = next(n for n in register.normen if n.geltung is KanalkapazitaetGeltung.KAPAZITIV)

        self.assertEqual(norm.kanalkapazitaet_typ, KanalkapazitaetTyp.ORDNUNGS_KANALKAPAZITAET)
        self.assertEqual(norm.prozedur, KanalkapazitaetProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kanalkapazitaet_weight, 0.0)

    def test_kki_kanalkapazitaet_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_kanalkapazitaet_register(register_id="register-372-expansion")
        norm = next(n for n in register.normen if n.geltung is KanalkapazitaetGeltung.GRUNDLEGEND_KAPAZITIV)

        self.assertEqual(norm.kanalkapazitaet_typ, KanalkapazitaetTyp.SOUVERAENITAETS_KANALKAPAZITAET)
        self.assertEqual(norm.prozedur, KanalkapazitaetProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.kanalkapazitaet_weight, 0.0)

    def test_kki_kanalkapazitaet_register_aggregates_register_signal(self) -> None:
        register = build_kanalkapazitaet_register(register_id="register-372-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-372-signal-stability-lane",))
        self.assertEqual(register.kapazitiv_norm_ids, ("register-372-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-372-signal-expansion-lane",))

    # #373 QuantenBitKodex
    def test_kki_quanten_bit_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_quanten_bit_kodex(kodex_id="kodex-373-stability")
        norm = next(n for n in kodex.normen if n.geltung is QuantenBitGeltung.GESPERRT)

        self.assertIsInstance(kodex, QuantenBitKodex)
        self.assertIsInstance(norm, QuantenBitNorm)
        self.assertEqual(norm.quanten_bit_typ, QuantenBitTyp.SCHUTZ_QUANTEN_BIT)
        self.assertEqual(norm.prozedur, QuantenBitProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.quanten_bit_tier, 1)

    def test_kki_quanten_bit_kodex_builds_superponiert_ordnungs_norm(self) -> None:
        kodex = build_quanten_bit_kodex(kodex_id="kodex-373-governance")
        norm = next(n for n in kodex.normen if n.geltung is QuantenBitGeltung.SUPERPONIERT)

        self.assertEqual(norm.quanten_bit_typ, QuantenBitTyp.ORDNUNGS_QUANTEN_BIT)
        self.assertEqual(norm.prozedur, QuantenBitProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.quanten_bit_weight, 0.0)

    def test_kki_quanten_bit_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_quanten_bit_kodex(kodex_id="kodex-373-expansion")
        norm = next(n for n in kodex.normen if n.geltung is QuantenBitGeltung.GRUNDLEGEND_SUPERPONIERT)

        self.assertEqual(norm.quanten_bit_typ, QuantenBitTyp.SOUVERAENITAETS_QUANTEN_BIT)
        self.assertEqual(norm.prozedur, QuantenBitProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.quanten_bit_weight, 0.0)

    def test_kki_quanten_bit_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_quanten_bit_kodex(kodex_id="kodex-373-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-373-signal-stability-lane",))
        self.assertEqual(kodex.superponiert_norm_ids, ("kodex-373-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-373-signal-expansion-lane",))

    # #374 VerschraenkungCharta
    def test_kki_verschraenkung_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_verschraenkung_charta(charta_id="charta-374-stability")
        norm = next(n for n in charta.normen if n.geltung is VerschraenkungGeltung.GESPERRT)

        self.assertIsInstance(charta, VerschraenkungCharta)
        self.assertIsInstance(norm, VerschraenkungNorm)
        self.assertEqual(norm.verschraenkung_typ, VerschraenkungTyp.SCHUTZ_VERSCHRAENKUNG)
        self.assertEqual(norm.prozedur, VerschraenkungProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.verschraenkung_tier, 1)

    def test_kki_verschraenkung_charta_builds_verschraenkt_ordnungs_norm(self) -> None:
        charta = build_verschraenkung_charta(charta_id="charta-374-governance")
        norm = next(n for n in charta.normen if n.geltung is VerschraenkungGeltung.VERSCHRAENKT)

        self.assertEqual(norm.verschraenkung_typ, VerschraenkungTyp.ORDNUNGS_VERSCHRAENKUNG)
        self.assertEqual(norm.prozedur, VerschraenkungProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.verschraenkung_weight, 0.0)

    def test_kki_verschraenkung_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_verschraenkung_charta(charta_id="charta-374-expansion")
        norm = next(n for n in charta.normen if n.geltung is VerschraenkungGeltung.GRUNDLEGEND_VERSCHRAENKT)

        self.assertEqual(norm.verschraenkung_typ, VerschraenkungTyp.SOUVERAENITAETS_VERSCHRAENKUNG)
        self.assertEqual(norm.prozedur, VerschraenkungProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.verschraenkung_weight, 0.0)

    def test_kki_verschraenkung_charta_aggregates_charta_signal(self) -> None:
        charta = build_verschraenkung_charta(charta_id="charta-374-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-374-signal-stability-lane",))
        self.assertEqual(charta.verschraenkt_norm_ids, ("charta-374-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-374-signal-expansion-lane",))


    # #375 QuantenfehlerPakt
    def test_kki_quantenfehler_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_quantenfehler_pakt(pakt_id="pakt-375-stability")
        norm = next(n for n in pakt.normen if n.geltung is QuantenfehlerGeltung.GESPERRT)

        self.assertIsInstance(pakt, QuantenfehlerPakt)
        self.assertIsInstance(norm, QuantenfehlerNorm)
        self.assertEqual(norm.quantenfehler_typ, QuantenfehlerTyp.SCHUTZ_QUANTENFEHLER)
        self.assertEqual(norm.prozedur, QuantenfehlerProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.quantenfehler_tier, 1)

    def test_kki_quantenfehler_pakt_builds_fehlerkorrigiert_ordnungs_norm(self) -> None:
        pakt = build_quantenfehler_pakt(pakt_id="pakt-375-governance")
        norm = next(n for n in pakt.normen if n.geltung is QuantenfehlerGeltung.FEHLERKORRIGIERT)

        self.assertEqual(norm.quantenfehler_typ, QuantenfehlerTyp.ORDNUNGS_QUANTENFEHLER)
        self.assertEqual(norm.prozedur, QuantenfehlerProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.quantenfehler_weight, 0.0)

    def test_kki_quantenfehler_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_quantenfehler_pakt(pakt_id="pakt-375-expansion")
        norm = next(n for n in pakt.normen if n.geltung is QuantenfehlerGeltung.GRUNDLEGEND_FEHLERKORRIGIERT)

        self.assertEqual(norm.quantenfehler_typ, QuantenfehlerTyp.SOUVERAENITAETS_QUANTENFEHLER)
        self.assertEqual(norm.prozedur, QuantenfehlerProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.quantenfehler_weight, 0.0)

    def test_kki_quantenfehler_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_quantenfehler_pakt(pakt_id="pakt-375-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-375-signal-stability-lane",))
        self.assertEqual(pakt.fehlerkorrigiert_norm_ids, ("pakt-375-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-375-signal-expansion-lane",))

    # #376 QuantenkryptoSenat
    def test_kki_quantenkrypto_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_quantenkrypto_senat(senat_id="senat-376-stability")
        norm = next(n for n in senat.normen if n.geltung is QuantenkryptoGeltung.GESPERRT)

        self.assertIsInstance(senat, QuantenkryptoSenat)
        self.assertIsInstance(norm, QuantenkryptoNorm)
        self.assertEqual(norm.quantenkrypto_typ, QuantenkryptoTyp.SCHUTZ_QUANTENKRYPTO)
        self.assertEqual(norm.prozedur, QuantenkryptoProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.quantenkrypto_tier, 1)

    def test_kki_quantenkrypto_senat_builds_quantengesichert_ordnungs_norm(self) -> None:
        senat = build_quantenkrypto_senat(senat_id="senat-376-governance")
        norm = next(n for n in senat.normen if n.geltung is QuantenkryptoGeltung.QUANTENGESICHERT)

        self.assertEqual(norm.quantenkrypto_typ, QuantenkryptoTyp.ORDNUNGS_QUANTENKRYPTO)
        self.assertEqual(norm.prozedur, QuantenkryptoProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.quantenkrypto_weight, 0.0)

    def test_kki_quantenkrypto_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_quantenkrypto_senat(senat_id="senat-376-expansion")
        norm = next(n for n in senat.normen if n.geltung is QuantenkryptoGeltung.GRUNDLEGEND_QUANTENGESICHERT)

        self.assertEqual(norm.quantenkrypto_typ, QuantenkryptoTyp.SOUVERAENITAETS_QUANTENKRYPTO)
        self.assertEqual(norm.prozedur, QuantenkryptoProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.quantenkrypto_weight, 0.0)

    def test_kki_quantenkrypto_senat_aggregates_senat_signal(self) -> None:
        senat = build_quantenkrypto_senat(senat_id="senat-376-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-376-signal-stability-lane",))
        self.assertEqual(senat.quantengesichert_norm_ids, ("senat-376-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-376-signal-expansion-lane",))

    # #377 HolographischesPrinzipNorm
    def test_kki_holographisches_prinzip_norm_builds_gesperrt_schutz_norm(self) -> None:
        satz = build_holographisches_prinzip_norm(norm_id="norm-377-stability")
        norm = next(n for n in satz.normen if n.geltung is HolographischesPrinzipNormGeltung.GESPERRT)

        self.assertIsInstance(satz, HolographischesPrinzipNormSatz)
        self.assertIsInstance(norm, HolographischesPrinzipNormEintrag)
        self.assertEqual(norm.holographisches_prinzip_norm_typ, HolographischesPrinzipNormTyp.SCHUTZ_HOLOGRAPHISCHES_PRINZIP_NORM)
        self.assertEqual(norm.prozedur, HolographischesPrinzipNormProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.holographisches_prinzip_norm_tier, 1)

    def test_kki_holographisches_prinzip_norm_builds_holographisch_ordnungs_norm(self) -> None:
        satz = build_holographisches_prinzip_norm(norm_id="norm-377-governance")
        norm = next(n for n in satz.normen if n.geltung is HolographischesPrinzipNormGeltung.HOLOGRAPHISCH)

        self.assertEqual(norm.holographisches_prinzip_norm_typ, HolographischesPrinzipNormTyp.ORDNUNGS_HOLOGRAPHISCHES_PRINZIP_NORM)
        self.assertEqual(norm.prozedur, HolographischesPrinzipNormProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.holographisches_prinzip_norm_weight, 0.0)

    def test_kki_holographisches_prinzip_norm_builds_grundlegend_souveraenitaets_norm(self) -> None:
        satz = build_holographisches_prinzip_norm(norm_id="norm-377-expansion")
        norm = next(n for n in satz.normen if n.geltung is HolographischesPrinzipNormGeltung.GRUNDLEGEND_HOLOGRAPHISCH)

        self.assertEqual(norm.holographisches_prinzip_norm_typ, HolographischesPrinzipNormTyp.SOUVERAENITAETS_HOLOGRAPHISCHES_PRINZIP_NORM)
        self.assertEqual(norm.prozedur, HolographischesPrinzipNormProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.holographisches_prinzip_norm_weight, 0.0)

    def test_kki_holographisches_prinzip_norm_aggregates_norm_signal(self) -> None:
        satz = build_holographisches_prinzip_norm(norm_id="norm-377-signal")

        self.assertEqual(satz.norm_signal.status, "norm-gesperrt")
        self.assertEqual(satz.gesperrt_norm_ids, ("norm-377-signal-stability-lane",))
        self.assertEqual(satz.holographisch_norm_ids, ("norm-377-signal-governance-lane",))
        self.assertEqual(satz.grundlegend_norm_ids, ("norm-377-signal-expansion-lane",))

    # #378 LandauerManifest
    def test_kki_landauer_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_landauer_manifest(manifest_id="manifest-378-stability")
        norm = next(n for n in manifest.normen if n.geltung is LandauerGeltung.GESPERRT)

        self.assertIsInstance(manifest, LandauerManifest)
        self.assertIsInstance(norm, LandauerNorm)
        self.assertEqual(norm.landauer_typ, LandauerTyp.SCHUTZ_LANDAUER)
        self.assertEqual(norm.prozedur, LandauerProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.landauer_tier, 1)

    def test_kki_landauer_manifest_builds_landauergebunden_ordnungs_norm(self) -> None:
        manifest = build_landauer_manifest(manifest_id="manifest-378-governance")
        norm = next(n for n in manifest.normen if n.geltung is LandauerGeltung.LANDAUERGEBUNDEN)

        self.assertEqual(norm.landauer_typ, LandauerTyp.ORDNUNGS_LANDAUER)
        self.assertEqual(norm.prozedur, LandauerProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.landauer_weight, 0.0)

    def test_kki_landauer_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_landauer_manifest(manifest_id="manifest-378-expansion")
        norm = next(n for n in manifest.normen if n.geltung is LandauerGeltung.GRUNDLEGEND_LANDAUERGEBUNDEN)

        self.assertEqual(norm.landauer_typ, LandauerTyp.SOUVERAENITAETS_LANDAUER)
        self.assertEqual(norm.prozedur, LandauerProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.landauer_weight, 0.0)

    def test_kki_landauer_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_landauer_manifest(manifest_id="manifest-378-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-378-signal-stability-lane",))
        self.assertEqual(manifest.landauergebunden_norm_ids, ("manifest-378-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-378-signal-expansion-lane",))

    # #379 NoCloningKodex
    def test_kki_no_cloning_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_no_cloning_kodex(kodex_id="kodex-379-stability")
        norm = next(n for n in kodex.normen if n.geltung is NoCloningGeltung.GESPERRT)

        self.assertIsInstance(kodex, NoCloningKodex)
        self.assertIsInstance(norm, NoCloningNorm)
        self.assertEqual(norm.no_cloning_typ, NoCloningTyp.SCHUTZ_NO_CLONING)
        self.assertEqual(norm.prozedur, NoCloningProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.no_cloning_tier, 1)

    def test_kki_no_cloning_kodex_builds_nichtklonbar_ordnungs_norm(self) -> None:
        kodex = build_no_cloning_kodex(kodex_id="kodex-379-governance")
        norm = next(n for n in kodex.normen if n.geltung is NoCloningGeltung.NICHTKLONBAR)

        self.assertEqual(norm.no_cloning_typ, NoCloningTyp.ORDNUNGS_NO_CLONING)
        self.assertEqual(norm.prozedur, NoCloningProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.no_cloning_weight, 0.0)

    def test_kki_no_cloning_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_no_cloning_kodex(kodex_id="kodex-379-expansion")
        norm = next(n for n in kodex.normen if n.geltung is NoCloningGeltung.GRUNDLEGEND_NICHTKLONBAR)

        self.assertEqual(norm.no_cloning_typ, NoCloningTyp.SOUVERAENITAETS_NO_CLONING)
        self.assertEqual(norm.prozedur, NoCloningProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.no_cloning_weight, 0.0)

    def test_kki_no_cloning_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_no_cloning_kodex(kodex_id="kodex-379-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-379-signal-stability-lane",))
        self.assertEqual(kodex.nichtklonbar_norm_ids, ("kodex-379-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-379-signal-expansion-lane",))

    # #380 QuanteninformationsVerfassung (Block-Krone)
    def test_kki_quanteninformations_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_quanteninformations_verfassung(verfassung_id="verfassung-380-stability")
        norm = next(n for n in verfassung.normen if n.geltung is QuanteninformationsVerfassungsGeltung.GESPERRT)

        self.assertIsInstance(verfassung, QuanteninformationsVerfassung)
        self.assertIsInstance(norm, QuanteninformationsVerfassungsNorm)
        self.assertEqual(norm.quanteninformations_verfassungs_typ, QuanteninformationsVerfassungsTyp.SCHUTZ_QUANTENINFORMATIONSVERFASSUNG)
        self.assertEqual(norm.prozedur, QuanteninformationsVerfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.quanteninformations_verfassungs_tier, 1)

    def test_kki_quanteninformations_verfassung_builds_quantenverfasst_ordnungs_norm(self) -> None:
        verfassung = build_quanteninformations_verfassung(verfassung_id="verfassung-380-governance")
        norm = next(n for n in verfassung.normen if n.geltung is QuanteninformationsVerfassungsGeltung.QUANTENVERFASST)

        self.assertEqual(norm.quanteninformations_verfassungs_typ, QuanteninformationsVerfassungsTyp.ORDNUNGS_QUANTENINFORMATIONSVERFASSUNG)
        self.assertEqual(norm.prozedur, QuanteninformationsVerfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.quanteninformations_verfassungs_weight, 0.0)

    def test_kki_quanteninformations_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_quanteninformations_verfassung(verfassung_id="verfassung-380-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is QuanteninformationsVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST)

        self.assertEqual(norm.quanteninformations_verfassungs_typ, QuanteninformationsVerfassungsTyp.SOUVERAENITAETS_QUANTENINFORMATIONSVERFASSUNG)
        self.assertEqual(norm.prozedur, QuanteninformationsVerfassungsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.quanteninformations_verfassungs_weight, 0.0)

    def test_kki_quanteninformations_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_quanteninformations_verfassung(verfassung_id="verfassung-380-signal")

        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-380-signal-stability-lane",))
        self.assertEqual(verfassung.quantenverfasst_norm_ids, ("verfassung-380-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-380-signal-expansion-lane",))

    # #381 BiophysikFeld
    def test_kki_biophysik_feld_builds_gesperrt_schutz_norm(self) -> None:
        feld = build_biophysik_feld(feld_id="feld-381-stability")
        norm = next(n for n in feld.normen if n.geltung is BiophysikGeltung.GESPERRT)

        self.assertIsInstance(feld, BiophysikFeld)
        self.assertIsInstance(norm, BiophysikNorm)
        self.assertEqual(norm.biophysik_typ, BiophysikTyp.SCHUTZ_BIOPHYSIK)
        self.assertEqual(norm.prozedur, BiophysikProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.biophysik_tier, 1)

    def test_kki_biophysik_feld_builds_biophysikalisch_ordnungs_norm(self) -> None:
        feld = build_biophysik_feld(feld_id="feld-381-governance")
        norm = next(n for n in feld.normen if n.geltung is BiophysikGeltung.BIOPHYSIKALISCH)

        self.assertEqual(norm.biophysik_typ, BiophysikTyp.ORDNUNGS_BIOPHYSIK)
        self.assertEqual(norm.prozedur, BiophysikProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.biophysik_weight, 0.0)

    def test_kki_biophysik_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        feld = build_biophysik_feld(feld_id="feld-381-expansion")
        norm = next(n for n in feld.normen if n.geltung is BiophysikGeltung.GRUNDLEGEND_BIOPHYSIKALISCH)

        self.assertEqual(norm.biophysik_typ, BiophysikTyp.SOUVERAENITAETS_BIOPHYSIK)
        self.assertEqual(norm.prozedur, BiophysikProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.biophysik_weight, 0.0)

    def test_kki_biophysik_feld_aggregates_feld_signal(self) -> None:
        feld = build_biophysik_feld(feld_id="feld-381-signal")

        self.assertEqual(feld.feld_signal.status, "feld-gesperrt")
        self.assertEqual(feld.gesperrt_norm_ids, ("feld-381-signal-stability-lane",))
        self.assertEqual(feld.biophysikalisch_norm_ids, ("feld-381-signal-governance-lane",))
        self.assertEqual(feld.grundlegend_norm_ids, ("feld-381-signal-expansion-lane",))

    # #382 DnaReplikationRegister
    def test_kki_dna_replikation_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_dna_replikation_register(register_id="register-382-stability")
        norm = next(n for n in register.normen if n.geltung is DnaReplikationGeltung.GESPERRT)

        self.assertIsInstance(register, DnaReplikationRegister)
        self.assertIsInstance(norm, DnaReplikationNorm)
        self.assertEqual(norm.dna_replikation_typ, DnaReplikationTyp.SCHUTZ_DNA_REPLIKATION)
        self.assertEqual(norm.prozedur, DnaReplikationProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.dna_replikation_tier, 1)

    def test_kki_dna_replikation_register_builds_dnarepliiert_ordnungs_norm(self) -> None:
        register = build_dna_replikation_register(register_id="register-382-governance")
        norm = next(n for n in register.normen if n.geltung is DnaReplikationGeltung.DNAREPLIIERT)

        self.assertEqual(norm.dna_replikation_typ, DnaReplikationTyp.ORDNUNGS_DNA_REPLIKATION)
        self.assertEqual(norm.prozedur, DnaReplikationProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.dna_replikation_weight, 0.0)

    def test_kki_dna_replikation_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_dna_replikation_register(register_id="register-382-expansion")
        norm = next(n for n in register.normen if n.geltung is DnaReplikationGeltung.GRUNDLEGEND_DNAREPLIIERT)

        self.assertEqual(norm.dna_replikation_typ, DnaReplikationTyp.SOUVERAENITAETS_DNA_REPLIKATION)
        self.assertEqual(norm.prozedur, DnaReplikationProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.dna_replikation_weight, 0.0)

    def test_kki_dna_replikation_register_aggregates_register_signal(self) -> None:
        register = build_dna_replikation_register(register_id="register-382-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-382-signal-stability-lane",))
        self.assertEqual(register.dnarepliiert_norm_ids, ("register-382-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-382-signal-expansion-lane",))

    # #383 ProteinfaltungCharta
    def test_kki_proteinfaltung_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_proteinfaltung_charta(charta_id="charta-383-stability")
        norm = next(n for n in charta.normen if n.geltung is ProteinfaltungGeltung.GESPERRT)

        self.assertIsInstance(charta, ProteinfaltungCharta)
        self.assertIsInstance(norm, ProteinfaltungNorm)
        self.assertEqual(norm.proteinfaltung_typ, ProteinfaltungTyp.SCHUTZ_PROTEINFALTUNG)
        self.assertEqual(norm.prozedur, ProteinfaltungProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.proteinfaltung_tier, 1)

    def test_kki_proteinfaltung_charta_builds_proteingefaltet_ordnungs_norm(self) -> None:
        charta = build_proteinfaltung_charta(charta_id="charta-383-governance")
        norm = next(n for n in charta.normen if n.geltung is ProteinfaltungGeltung.PROTEINGEFALTET)

        self.assertEqual(norm.proteinfaltung_typ, ProteinfaltungTyp.ORDNUNGS_PROTEINFALTUNG)
        self.assertEqual(norm.prozedur, ProteinfaltungProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.proteinfaltung_weight, 0.0)

    def test_kki_proteinfaltung_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_proteinfaltung_charta(charta_id="charta-383-expansion")
        norm = next(n for n in charta.normen if n.geltung is ProteinfaltungGeltung.GRUNDLEGEND_PROTEINGEFALTET)

        self.assertEqual(norm.proteinfaltung_typ, ProteinfaltungTyp.SOUVERAENITAETS_PROTEINFALTUNG)
        self.assertEqual(norm.prozedur, ProteinfaltungProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.proteinfaltung_weight, 0.0)

    def test_kki_proteinfaltung_charta_aggregates_charta_signal(self) -> None:
        charta = build_proteinfaltung_charta(charta_id="charta-383-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-383-signal-stability-lane",))
        self.assertEqual(charta.proteingefaltet_norm_ids, ("charta-383-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-383-signal-expansion-lane",))

    # #384 HodgkinHuxleyKodex
    def test_kki_hodgkin_huxley_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_hodgkin_huxley_kodex(kodex_id="kodex-384-stability")
        norm = next(n for n in kodex.normen if n.geltung is HodgkinHuxleyGeltung.GESPERRT)

        self.assertIsInstance(kodex, HodgkinHuxleyKodex)
        self.assertIsInstance(norm, HodgkinHuxleyNorm)
        self.assertEqual(norm.hodgkin_huxley_typ, HodgkinHuxleyTyp.SCHUTZ_HODGKIN_HUXLEY)
        self.assertEqual(norm.prozedur, HodgkinHuxleyProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.hodgkin_huxley_tier, 1)

    def test_kki_hodgkin_huxley_kodex_builds_aktionspotentiell_ordnungs_norm(self) -> None:
        kodex = build_hodgkin_huxley_kodex(kodex_id="kodex-384-governance")
        norm = next(n for n in kodex.normen if n.geltung is HodgkinHuxleyGeltung.AKTIONSPOTENTIELL)

        self.assertEqual(norm.hodgkin_huxley_typ, HodgkinHuxleyTyp.ORDNUNGS_HODGKIN_HUXLEY)
        self.assertEqual(norm.prozedur, HodgkinHuxleyProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.hodgkin_huxley_weight, 0.0)

    def test_kki_hodgkin_huxley_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_hodgkin_huxley_kodex(kodex_id="kodex-384-expansion")
        norm = next(n for n in kodex.normen if n.geltung is HodgkinHuxleyGeltung.GRUNDLEGEND_AKTIONSPOTENTIELL)

        self.assertEqual(norm.hodgkin_huxley_typ, HodgkinHuxleyTyp.SOUVERAENITAETS_HODGKIN_HUXLEY)
        self.assertEqual(norm.prozedur, HodgkinHuxleyProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.hodgkin_huxley_weight, 0.0)

    def test_kki_hodgkin_huxley_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_hodgkin_huxley_kodex(kodex_id="kodex-384-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-384-signal-stability-lane",))
        self.assertEqual(kodex.aktionspotentiell_norm_ids, ("kodex-384-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-384-signal-expansion-lane",))

    # #385 SynaptischePlastizitaetPakt
    def test_kki_synaptische_plastizitaet_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_synaptische_plastizitaet_pakt(pakt_id="pakt-385-stability")
        norm = next(n for n in pakt.normen if n.geltung is SynaptischePlastizitaetGeltung.GESPERRT)

        self.assertIsInstance(pakt, SynaptischePlastizitaetPakt)
        self.assertIsInstance(norm, SynaptischePlastizitaetNorm)
        self.assertEqual(norm.synaptische_plastizitaet_typ, SynaptischePlastizitaetTyp.SCHUTZ_SYNAPTISCHE_PLASTIZITAET)
        self.assertEqual(norm.prozedur, SynaptischePlastizitaetProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.synaptische_plastizitaet_tier, 1)

    def test_kki_synaptische_plastizitaet_pakt_builds_synaptischplastisch_ordnungs_norm(self) -> None:
        pakt = build_synaptische_plastizitaet_pakt(pakt_id="pakt-385-governance")
        norm = next(n for n in pakt.normen if n.geltung is SynaptischePlastizitaetGeltung.SYNAPTISCHPLASTISCH)

        self.assertEqual(norm.synaptische_plastizitaet_typ, SynaptischePlastizitaetTyp.ORDNUNGS_SYNAPTISCHE_PLASTIZITAET)
        self.assertEqual(norm.prozedur, SynaptischePlastizitaetProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.synaptische_plastizitaet_weight, 0.0)

    def test_kki_synaptische_plastizitaet_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_synaptische_plastizitaet_pakt(pakt_id="pakt-385-expansion")
        norm = next(n for n in pakt.normen if n.geltung is SynaptischePlastizitaetGeltung.GRUNDLEGEND_SYNAPTISCHPLASTISCH)

        self.assertEqual(norm.synaptische_plastizitaet_typ, SynaptischePlastizitaetTyp.SOUVERAENITAETS_SYNAPTISCHE_PLASTIZITAET)
        self.assertEqual(norm.prozedur, SynaptischePlastizitaetProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.synaptische_plastizitaet_weight, 0.0)

    def test_kki_synaptische_plastizitaet_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_synaptische_plastizitaet_pakt(pakt_id="pakt-385-signal")

        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-385-signal-stability-lane",))
        self.assertEqual(pakt.synaptischplastisch_norm_ids, ("pakt-385-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-385-signal-expansion-lane",))

    # #386 EvolutionManifest
    def test_kki_evolution_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_evolution_manifest(manifest_id="manifest-386-stability")
        norm = next(n for n in manifest.normen if n.geltung is EvolutionGeltung.GESPERRT)

        self.assertIsInstance(manifest, EvolutionManifest)
        self.assertIsInstance(norm, EvolutionNorm)
        self.assertEqual(norm.evolution_typ, EvolutionTyp.SCHUTZ_EVOLUTION)
        self.assertEqual(norm.prozedur, EvolutionProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.evolution_tier, 1)

    def test_kki_evolution_manifest_builds_evolutionaer_ordnungs_norm(self) -> None:
        manifest = build_evolution_manifest(manifest_id="manifest-386-governance")
        norm = next(n for n in manifest.normen if n.geltung is EvolutionGeltung.EVOLUTIONAER)

        self.assertEqual(norm.evolution_typ, EvolutionTyp.ORDNUNGS_EVOLUTION)
        self.assertEqual(norm.prozedur, EvolutionProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.evolution_weight, 0.0)

    def test_kki_evolution_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_evolution_manifest(manifest_id="manifest-386-expansion")
        norm = next(n for n in manifest.normen if n.geltung is EvolutionGeltung.GRUNDLEGEND_EVOLUTIONAER)

        self.assertEqual(norm.evolution_typ, EvolutionTyp.SOUVERAENITAETS_EVOLUTION)
        self.assertEqual(norm.prozedur, EvolutionProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.evolution_weight, 0.0)

    def test_kki_evolution_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_evolution_manifest(manifest_id="manifest-386-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-386-signal-stability-lane",))
        self.assertEqual(manifest.evolutionaer_norm_ids, ("manifest-386-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-386-signal-expansion-lane",))

    # #387 HomoostaseSenat
    def test_kki_homoostase_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_homoostase_senat(senat_id="senat-387-stability")
        norm = next(n for n in senat.normen if n.geltung is HomoostaseGeltung.GESPERRT)

        self.assertIsInstance(senat, HomoostaseSenat)
        self.assertIsInstance(norm, HomoostaseNorm)
        self.assertEqual(norm.homoostase_typ, HomoostaseTyp.SCHUTZ_HOMOOSTASE)
        self.assertEqual(norm.prozedur, HomoostasProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.homoostase_tier, 1)

    def test_kki_homoostase_senat_builds_homoostatisch_ordnungs_norm(self) -> None:
        senat = build_homoostase_senat(senat_id="senat-387-governance")
        norm = next(n for n in senat.normen if n.geltung is HomoostaseGeltung.HOMOOSTATISCH)

        self.assertEqual(norm.homoostase_typ, HomoostaseTyp.ORDNUNGS_HOMOOSTASE)
        self.assertEqual(norm.prozedur, HomoostasProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.homoostase_weight, 0.0)

    def test_kki_homoostase_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_homoostase_senat(senat_id="senat-387-expansion")
        norm = next(n for n in senat.normen if n.geltung is HomoostaseGeltung.GRUNDLEGEND_HOMOOSTATISCH)

        self.assertEqual(norm.homoostase_typ, HomoostaseTyp.SOUVERAENITAETS_HOMOOSTASE)
        self.assertEqual(norm.prozedur, HomoostasProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.homoostase_weight, 0.0)

    def test_kki_homoostase_senat_aggregates_senat_signal(self) -> None:
        senat = build_homoostase_senat(senat_id="senat-387-signal")

        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-387-signal-stability-lane",))
        self.assertEqual(senat.homoostatisch_norm_ids, ("senat-387-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-387-signal-expansion-lane",))

    # #388 LotkaVolterraNorm (*_norm)
    def test_kki_lotka_volterra_norm_builds_gesperrt_schutz_eintrag(self) -> None:
        satz = build_lotka_volterra_norm(norm_id="norm-388-stability")
        eintrag = next(n for n in satz.normen if n.geltung is LotkaVolterraNormGeltung.GESPERRT)

        self.assertIsInstance(satz, LotkaVolterraNormSatz)
        self.assertIsInstance(eintrag, LotkaVolterraNormEintrag)
        self.assertEqual(eintrag.lotka_volterra_norm_typ, LotkaVolterraNormTyp.SCHUTZ_LOTKA_VOLTERRA_NORM)
        self.assertEqual(eintrag.prozedur, LotkaVolterraNormProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.lotka_volterra_norm_tier, 1)

    def test_kki_lotka_volterra_norm_builds_lotkavolterrabeschr_ordnungs_eintrag(self) -> None:
        satz = build_lotka_volterra_norm(norm_id="norm-388-governance")
        eintrag = next(n for n in satz.normen if n.geltung is LotkaVolterraNormGeltung.LOTKAVOLTERRABESCHR)

        self.assertEqual(eintrag.lotka_volterra_norm_typ, LotkaVolterraNormTyp.ORDNUNGS_LOTKA_VOLTERRA_NORM)
        self.assertEqual(eintrag.prozedur, LotkaVolterraNormProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.lotka_volterra_norm_weight, 0.0)

    def test_kki_lotka_volterra_norm_builds_grundlegend_souveraenitaets_eintrag(self) -> None:
        satz = build_lotka_volterra_norm(norm_id="norm-388-expansion")
        eintrag = next(n for n in satz.normen if n.geltung is LotkaVolterraNormGeltung.GRUNDLEGEND_LOTKAVOLTERRABESCHR)

        self.assertEqual(eintrag.lotka_volterra_norm_typ, LotkaVolterraNormTyp.SOUVERAENITAETS_LOTKA_VOLTERRA_NORM)
        self.assertEqual(eintrag.prozedur, LotkaVolterraNormProzedur.PLENARPROTOKOLL)
        self.assertGreater(eintrag.lotka_volterra_norm_weight, 0.0)

    def test_kki_lotka_volterra_norm_aggregates_norm_signal(self) -> None:
        satz = build_lotka_volterra_norm(norm_id="norm-388-signal")

        self.assertEqual(satz.norm_signal.status, "norm-gesperrt")
        self.assertEqual(satz.gesperrt_norm_ids, ("norm-388-signal-stability-lane",))
        self.assertEqual(satz.lotkavolterrabeschr_norm_ids, ("norm-388-signal-governance-lane",))
        self.assertEqual(satz.grundlegend_norm_ids, ("norm-388-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #389 MorphogeneseCharta
    # ------------------------------------------------------------------

    def test_kki_morphogenese_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_morphogenese_charta(charta_id="charta-389-stability")
        norm = next(n for n in charta.normen if n.geltung is MorphogeneseGeltung.GESPERRT)

        self.assertEqual(norm.morphogenese_typ, MorphogeneseTyp.SCHUTZ_MORPHOGENESE)
        self.assertEqual(norm.prozedur, MorphogeneseProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.morphogenese_tier, 1)

    def test_kki_morphogenese_charta_builds_morphogenetisch_ordnungs_norm(self) -> None:
        charta = build_morphogenese_charta(charta_id="charta-389-governance")
        norm = next(n for n in charta.normen if n.geltung is MorphogeneseGeltung.MORPHOGENETISCH)

        self.assertEqual(norm.morphogenese_typ, MorphogeneseTyp.ORDNUNGS_MORPHOGENESE)
        self.assertEqual(norm.prozedur, MorphogeneseProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.morphogenese_weight, 0.0)

    def test_kki_morphogenese_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_morphogenese_charta(charta_id="charta-389-expansion")
        norm = next(n for n in charta.normen if n.geltung is MorphogeneseGeltung.GRUNDLEGEND_MORPHOGENETISCH)

        self.assertEqual(norm.morphogenese_typ, MorphogeneseTyp.SOUVERAENITAETS_MORPHOGENESE)
        self.assertEqual(norm.prozedur, MorphogeneseProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.morphogenese_weight, 0.0)

    def test_kki_morphogenese_charta_aggregates_charta_signal(self) -> None:
        charta = build_morphogenese_charta(charta_id="charta-389-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-389-signal-stability-lane",))
        self.assertEqual(charta.morphogenetisch_norm_ids, ("charta-389-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-389-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #390 SystembiologieVerfassung (Block-Krone)
    # ------------------------------------------------------------------

    def test_kki_systembiologie_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_systembiologie_verfassung(verfassung_id="verfassung-390-stability")
        norm = next(n for n in verfassung.normen if n.geltung is SystembiologieVerfassungsGeltung.GESPERRT)

        self.assertEqual(norm.systembiologie_verfassungs_typ, SystembiologieVerfassungsTyp.SCHUTZ_SYSTEMBIOLOGIEVERFASSUNG)
        self.assertEqual(norm.prozedur, SystembiologieVerfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.systembiologie_verfassungs_tier, 1)

    def test_kki_systembiologie_verfassung_builds_systembiologieverfasst_ordnungs_norm(self) -> None:
        verfassung = build_systembiologie_verfassung(verfassung_id="verfassung-390-governance")
        norm = next(n for n in verfassung.normen if n.geltung is SystembiologieVerfassungsGeltung.SYSTEMBIOLOGIEVERFASST)

        self.assertEqual(norm.systembiologie_verfassungs_typ, SystembiologieVerfassungsTyp.ORDNUNGS_SYSTEMBIOLOGIEVERFASSUNG)
        self.assertEqual(norm.prozedur, SystembiologieVerfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.systembiologie_verfassungs_weight, 0.0)

    def test_kki_systembiologie_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_systembiologie_verfassung(verfassung_id="verfassung-390-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is SystembiologieVerfassungsGeltung.GRUNDLEGEND_SYSTEMBIOLOGIEVERFASST)

        self.assertEqual(norm.systembiologie_verfassungs_typ, SystembiologieVerfassungsTyp.SOUVERAENITAETS_SYSTEMBIOLOGIEVERFASSUNG)
        self.assertEqual(norm.prozedur, SystembiologieVerfassungsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.systembiologie_verfassungs_weight, 0.0)

    def test_kki_systembiologie_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_systembiologie_verfassung(verfassung_id="verfassung-390-signal")

        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-390-signal-stability-lane",))
        self.assertEqual(verfassung.systembiologieverfasst_norm_ids, ("verfassung-390-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-390-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #391 KognitionsFeld
    # ------------------------------------------------------------------

    def test_kki_kognitions_feld_builds_gesperrt_schutz_norm(self) -> None:
        feld = build_kognitions_feld(feld_id="feld-391-stability")
        norm = next(n for n in feld.normen if n.geltung is KognitionsGeltung.GESPERRT)
        self.assertEqual(norm.kognitions_typ, KognitionsTyp.SCHUTZ_KOGNITION)
        self.assertEqual(norm.prozedur, KognitionsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kognitions_tier, 1)

    def test_kki_kognitions_feld_builds_kognitiv_ordnungs_norm(self) -> None:
        feld = build_kognitions_feld(feld_id="feld-391-governance")
        norm = next(n for n in feld.normen if n.geltung is KognitionsGeltung.KOGNITIV)
        self.assertEqual(norm.kognitions_typ, KognitionsTyp.ORDNUNGS_KOGNITION)
        self.assertEqual(norm.prozedur, KognitionsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kognitions_weight, 0.0)

    def test_kki_kognitions_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        feld = build_kognitions_feld(feld_id="feld-391-expansion")
        norm = next(n for n in feld.normen if n.geltung is KognitionsGeltung.GRUNDLEGEND_KOGNITIV)
        self.assertEqual(norm.kognitions_typ, KognitionsTyp.SOUVERAENITAETS_KOGNITION)
        self.assertEqual(norm.prozedur, KognitionsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.kognitions_weight, 0.0)

    def test_kki_kognitions_feld_aggregates_feld_signal(self) -> None:
        feld = build_kognitions_feld(feld_id="feld-391-signal")
        self.assertEqual(feld.feld_signal.status, "feld-gesperrt")
        self.assertEqual(feld.gesperrt_norm_ids, ("feld-391-signal-stability-lane",))
        self.assertEqual(feld.kognitiv_norm_ids, ("feld-391-signal-governance-lane",))
        self.assertEqual(feld.grundlegend_norm_ids, ("feld-391-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #392 ArbeitsgedaechtnisRegister
    # ------------------------------------------------------------------

    def test_kki_arbeitsgedaechtnis_register_builds_gesperrt_schutz_norm(self) -> None:
        reg = build_arbeitsgedaechtnis_register(register_id="register-392-stability")
        norm = next(n for n in reg.normen if n.geltung is ArbeitsgedaechtnisGeltung.GESPERRT)
        self.assertEqual(norm.arbeitsgedaechtnis_typ, ArbeitsgedaechtnisTyp.SCHUTZ_ARBEITSGEDAECHTNIS)
        self.assertEqual(norm.prozedur, ArbeitsgedaechtnispProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.arbeitsgedaechtnis_tier, 1)

    def test_kki_arbeitsgedaechtnis_register_builds_arbeitsgedaechtnisaktiv_ordnungs_norm(self) -> None:
        reg = build_arbeitsgedaechtnis_register(register_id="register-392-governance")
        norm = next(n for n in reg.normen if n.geltung is ArbeitsgedaechtnisGeltung.ARBEITSGEDAECHTNISAKTIV)
        self.assertEqual(norm.arbeitsgedaechtnis_typ, ArbeitsgedaechtnisTyp.ORDNUNGS_ARBEITSGEDAECHTNIS)
        self.assertEqual(norm.prozedur, ArbeitsgedaechtnispProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.arbeitsgedaechtnis_weight, 0.0)

    def test_kki_arbeitsgedaechtnis_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        reg = build_arbeitsgedaechtnis_register(register_id="register-392-expansion")
        norm = next(n for n in reg.normen if n.geltung is ArbeitsgedaechtnisGeltung.GRUNDLEGEND_ARBEITSGEDAECHTNISAKTIV)
        self.assertEqual(norm.arbeitsgedaechtnis_typ, ArbeitsgedaechtnisTyp.SOUVERAENITAETS_ARBEITSGEDAECHTNIS)
        self.assertEqual(norm.prozedur, ArbeitsgedaechtnispProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.arbeitsgedaechtnis_weight, 0.0)

    def test_kki_arbeitsgedaechtnis_register_aggregates_register_signal(self) -> None:
        reg = build_arbeitsgedaechtnis_register(register_id="register-392-signal")
        self.assertEqual(reg.register_signal.status, "register-gesperrt")
        self.assertEqual(reg.gesperrt_norm_ids, ("register-392-signal-stability-lane",))
        self.assertEqual(reg.arbeitsgedaechtnisaktiv_norm_ids, ("register-392-signal-governance-lane",))
        self.assertEqual(reg.grundlegend_norm_ids, ("register-392-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #393 AufmerksamkeitsCharta
    # ------------------------------------------------------------------

    def test_kki_aufmerksamkeits_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_aufmerksamkeits_charta(charta_id="charta-393-stability")
        norm = next(n for n in charta.normen if n.geltung is AufmerksamkeitsGeltung.GESPERRT)
        self.assertEqual(norm.aufmerksamkeits_typ, AufmerksamkeitsTyp.SCHUTZ_AUFMERKSAMKEIT)
        self.assertEqual(norm.prozedur, AufmerksamkeitsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.aufmerksamkeits_tier, 1)

    def test_kki_aufmerksamkeits_charta_builds_aufmerksamkeitsgeleitet_ordnungs_norm(self) -> None:
        charta = build_aufmerksamkeits_charta(charta_id="charta-393-governance")
        norm = next(n for n in charta.normen if n.geltung is AufmerksamkeitsGeltung.AUFMERKSAMKEITSGELEITET)
        self.assertEqual(norm.aufmerksamkeits_typ, AufmerksamkeitsTyp.ORDNUNGS_AUFMERKSAMKEIT)
        self.assertEqual(norm.prozedur, AufmerksamkeitsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.aufmerksamkeits_weight, 0.0)

    def test_kki_aufmerksamkeits_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_aufmerksamkeits_charta(charta_id="charta-393-expansion")
        norm = next(n for n in charta.normen if n.geltung is AufmerksamkeitsGeltung.GRUNDLEGEND_AUFMERKSAMKEITSGELEITET)
        self.assertEqual(norm.aufmerksamkeits_typ, AufmerksamkeitsTyp.SOUVERAENITAETS_AUFMERKSAMKEIT)
        self.assertEqual(norm.prozedur, AufmerksamkeitsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.aufmerksamkeits_weight, 0.0)

    def test_kki_aufmerksamkeits_charta_aggregates_charta_signal(self) -> None:
        charta = build_aufmerksamkeits_charta(charta_id="charta-393-signal")
        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-393-signal-stability-lane",))
        self.assertEqual(charta.aufmerksamkeitsgeleitet_norm_ids, ("charta-393-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-393-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #394 EntscheidungsKodex
    # ------------------------------------------------------------------

    def test_kki_entscheidungs_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_entscheidungs_kodex(kodex_id="kodex-394-stability")
        norm = next(n for n in kodex.normen if n.geltung is EntscheidungsGeltung.GESPERRT)
        self.assertEqual(norm.entscheidungs_typ, EntscheidungsTyp.SCHUTZ_ENTSCHEIDUNG)
        self.assertEqual(norm.prozedur, EntscheidungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.entscheidungs_tier, 1)

    def test_kki_entscheidungs_kodex_builds_entscheidungsaktiv_ordnungs_norm(self) -> None:
        kodex = build_entscheidungs_kodex(kodex_id="kodex-394-governance")
        norm = next(n for n in kodex.normen if n.geltung is EntscheidungsGeltung.ENTSCHEIDUNGSAKTIV)
        self.assertEqual(norm.entscheidungs_typ, EntscheidungsTyp.ORDNUNGS_ENTSCHEIDUNG)
        self.assertEqual(norm.prozedur, EntscheidungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.entscheidungs_weight, 0.0)

    def test_kki_entscheidungs_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_entscheidungs_kodex(kodex_id="kodex-394-expansion")
        norm = next(n for n in kodex.normen if n.geltung is EntscheidungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSAKTIV)
        self.assertEqual(norm.entscheidungs_typ, EntscheidungsTyp.SOUVERAENITAETS_ENTSCHEIDUNG)
        self.assertEqual(norm.prozedur, EntscheidungsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.entscheidungs_weight, 0.0)

    def test_kki_entscheidungs_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_entscheidungs_kodex(kodex_id="kodex-394-signal")
        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-394-signal-stability-lane",))
        self.assertEqual(kodex.entscheidungsaktiv_norm_ids, ("kodex-394-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-394-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #395 GedaechtnisKonsolidierungsPakt
    # ------------------------------------------------------------------

    def test_kki_gedaechtnis_konsolidierungs_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_gedaechtnis_konsolidierungs_pakt(pakt_id="pakt-395-stability")
        norm = next(n for n in pakt.normen if n.geltung is GedaechtnisKonsolidierungsGeltung.GESPERRT)
        self.assertEqual(norm.gedaechtnis_konsolidierungs_typ, GedaechtnisKonsolidierungsTyp.SCHUTZ_GEDAECHTNIS_KONSOLIDIERUNG)
        self.assertEqual(norm.prozedur, GedaechtnisKonsolidierungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.gedaechtnis_konsolidierungs_tier, 1)

    def test_kki_gedaechtnis_konsolidierungs_pakt_builds_konsolidiert_ordnungs_norm(self) -> None:
        pakt = build_gedaechtnis_konsolidierungs_pakt(pakt_id="pakt-395-governance")
        norm = next(n for n in pakt.normen if n.geltung is GedaechtnisKonsolidierungsGeltung.KONSOLIDIERT)
        self.assertEqual(norm.gedaechtnis_konsolidierungs_typ, GedaechtnisKonsolidierungsTyp.ORDNUNGS_GEDAECHTNIS_KONSOLIDIERUNG)
        self.assertEqual(norm.prozedur, GedaechtnisKonsolidierungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.gedaechtnis_konsolidierungs_weight, 0.0)

    def test_kki_gedaechtnis_konsolidierungs_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_gedaechtnis_konsolidierungs_pakt(pakt_id="pakt-395-expansion")
        norm = next(n for n in pakt.normen if n.geltung is GedaechtnisKonsolidierungsGeltung.GRUNDLEGEND_KONSOLIDIERT)
        self.assertEqual(norm.gedaechtnis_konsolidierungs_typ, GedaechtnisKonsolidierungsTyp.SOUVERAENITAETS_GEDAECHTNIS_KONSOLIDIERUNG)
        self.assertEqual(norm.prozedur, GedaechtnisKonsolidierungsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.gedaechtnis_konsolidierungs_weight, 0.0)

    def test_kki_gedaechtnis_konsolidierungs_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_gedaechtnis_konsolidierungs_pakt(pakt_id="pakt-395-signal")
        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-395-signal-stability-lane",))
        self.assertEqual(pakt.konsolidiert_norm_ids, ("pakt-395-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-395-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #396 SprachverarbeitungsManifest
    # ------------------------------------------------------------------

    def test_kki_sprachverarbeitungs_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_sprachverarbeitungs_manifest(manifest_id="manifest-396-stability")
        norm = next(n for n in manifest.normen if n.geltung is SprachverarbeitungsGeltung.GESPERRT)
        self.assertEqual(norm.sprachverarbeitungs_typ, SprachverarbeitungsTyp.SCHUTZ_SPRACHVERARBEITUNG)
        self.assertEqual(norm.prozedur, SprachverarbeitungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.sprachverarbeitungs_tier, 1)

    def test_kki_sprachverarbeitungs_manifest_builds_sprachverarbeitend_ordnungs_norm(self) -> None:
        manifest = build_sprachverarbeitungs_manifest(manifest_id="manifest-396-governance")
        norm = next(n for n in manifest.normen if n.geltung is SprachverarbeitungsGeltung.SPRACHVERARBEITEND)
        self.assertEqual(norm.sprachverarbeitungs_typ, SprachverarbeitungsTyp.ORDNUNGS_SPRACHVERARBEITUNG)
        self.assertEqual(norm.prozedur, SprachverarbeitungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.sprachverarbeitungs_weight, 0.0)

    def test_kki_sprachverarbeitungs_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_sprachverarbeitungs_manifest(manifest_id="manifest-396-expansion")
        norm = next(n for n in manifest.normen if n.geltung is SprachverarbeitungsGeltung.GRUNDLEGEND_SPRACHVERARBEITEND)
        self.assertEqual(norm.sprachverarbeitungs_typ, SprachverarbeitungsTyp.SOUVERAENITAETS_SPRACHVERARBEITUNG)
        self.assertEqual(norm.prozedur, SprachverarbeitungsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.sprachverarbeitungs_weight, 0.0)

    def test_kki_sprachverarbeitungs_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_sprachverarbeitungs_manifest(manifest_id="manifest-396-signal")
        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-396-signal-stability-lane",))
        self.assertEqual(manifest.sprachverarbeitend_norm_ids, ("manifest-396-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-396-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #397 BewusstseinsSenat
    # ------------------------------------------------------------------

    def test_kki_bewusstseins_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_bewusstseins_senat(senat_id="senat-397-stability")
        norm = next(n for n in senat.normen if n.geltung is BewusstseinsGeltung.GESPERRT)
        self.assertEqual(norm.bewusstseins_typ, BewusstseinsTyp.SCHUTZ_BEWUSSTSEIN)
        self.assertEqual(norm.prozedur, BewusstseinsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.bewusstseins_tier, 1)

    def test_kki_bewusstseins_senat_builds_bewusst_ordnungs_norm(self) -> None:
        senat = build_bewusstseins_senat(senat_id="senat-397-governance")
        norm = next(n for n in senat.normen if n.geltung is BewusstseinsGeltung.BEWUSST)
        self.assertEqual(norm.bewusstseins_typ, BewusstseinsTyp.ORDNUNGS_BEWUSSTSEIN)
        self.assertEqual(norm.prozedur, BewusstseinsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.bewusstseins_weight, 0.0)

    def test_kki_bewusstseins_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_bewusstseins_senat(senat_id="senat-397-expansion")
        norm = next(n for n in senat.normen if n.geltung is BewusstseinsGeltung.GRUNDLEGEND_BEWUSST)
        self.assertEqual(norm.bewusstseins_typ, BewusstseinsTyp.SOUVERAENITAETS_BEWUSSTSEIN)
        self.assertEqual(norm.prozedur, BewusstseinsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.bewusstseins_weight, 0.0)

    def test_kki_bewusstseins_senat_aggregates_senat_signal(self) -> None:
        senat = build_bewusstseins_senat(senat_id="senat-397-signal")
        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-397-signal-stability-lane",))
        self.assertEqual(senat.bewusst_norm_ids, ("senat-397-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-397-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #398 MetakognitionsNorm (*_norm)
    # ------------------------------------------------------------------

    def test_kki_metakognitions_norm_builds_gesperrt_schutz_eintrag(self) -> None:
        satz = build_metakognitions_norm(norm_id="norm-398-stability")
        eintrag = next(n for n in satz.normen if n.geltung is MetakognitionsNormGeltung.GESPERRT)
        self.assertEqual(eintrag.metakognitions_norm_typ, MetakognitionsNormTyp.SCHUTZ_METAKOGNITIONS_NORM)
        self.assertEqual(eintrag.prozedur, MetakognitionsNormProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.metakognitions_norm_tier, 1)

    def test_kki_metakognitions_norm_builds_metakognitiv_ordnungs_eintrag(self) -> None:
        satz = build_metakognitions_norm(norm_id="norm-398-governance")
        eintrag = next(n for n in satz.normen if n.geltung is MetakognitionsNormGeltung.METAKOGNITIV)
        self.assertEqual(eintrag.metakognitions_norm_typ, MetakognitionsNormTyp.ORDNUNGS_METAKOGNITIONS_NORM)
        self.assertEqual(eintrag.prozedur, MetakognitionsNormProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.metakognitions_norm_weight, 0.0)

    def test_kki_metakognitions_norm_builds_grundlegend_souveraenitaets_eintrag(self) -> None:
        satz = build_metakognitions_norm(norm_id="norm-398-expansion")
        eintrag = next(n for n in satz.normen if n.geltung is MetakognitionsNormGeltung.GRUNDLEGEND_METAKOGNITIV)
        self.assertEqual(eintrag.metakognitions_norm_typ, MetakognitionsNormTyp.SOUVERAENITAETS_METAKOGNITIONS_NORM)
        self.assertEqual(eintrag.prozedur, MetakognitionsNormProzedur.PLENARPROTOKOLL)
        self.assertGreater(eintrag.metakognitions_norm_weight, 0.0)

    def test_kki_metakognitions_norm_aggregates_norm_signal(self) -> None:
        satz = build_metakognitions_norm(norm_id="norm-398-signal")
        self.assertEqual(satz.norm_signal.status, "norm-gesperrt")
        self.assertEqual(satz.gesperrt_norm_ids, ("norm-398-signal-stability-lane",))
        self.assertEqual(satz.metakognitiv_norm_ids, ("norm-398-signal-governance-lane",))
        self.assertEqual(satz.grundlegend_norm_ids, ("norm-398-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #399 KognitiveFlexibilitaetsCharta
    # ------------------------------------------------------------------

    def test_kki_kognitive_flexibilitaets_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_kognitive_flexibilitaets_charta(charta_id="charta-399-stability")
        norm = next(n for n in charta.normen if n.geltung is KognitiveFlexibilitaetsGeltung.GESPERRT)
        self.assertEqual(norm.kognitive_flexibilitaets_typ, KognitiveFlexibilitaetsTyp.SCHUTZ_KOGNITIVE_FLEXIBILITAET)
        self.assertEqual(norm.prozedur, KognitiveFlexibilitaetsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kognitive_flexibilitaets_tier, 1)

    def test_kki_kognitive_flexibilitaets_charta_builds_kognitiv_flexibel_ordnungs_norm(self) -> None:
        charta = build_kognitive_flexibilitaets_charta(charta_id="charta-399-governance")
        norm = next(n for n in charta.normen if n.geltung is KognitiveFlexibilitaetsGeltung.KOGNITIV_FLEXIBEL)
        self.assertEqual(norm.kognitive_flexibilitaets_typ, KognitiveFlexibilitaetsTyp.ORDNUNGS_KOGNITIVE_FLEXIBILITAET)
        self.assertEqual(norm.prozedur, KognitiveFlexibilitaetsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kognitive_flexibilitaets_weight, 0.0)

    def test_kki_kognitive_flexibilitaets_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_kognitive_flexibilitaets_charta(charta_id="charta-399-expansion")
        norm = next(n for n in charta.normen if n.geltung is KognitiveFlexibilitaetsGeltung.GRUNDLEGEND_KOGNITIV_FLEXIBEL)
        self.assertEqual(norm.kognitive_flexibilitaets_typ, KognitiveFlexibilitaetsTyp.SOUVERAENITAETS_KOGNITIVE_FLEXIBILITAET)
        self.assertEqual(norm.prozedur, KognitiveFlexibilitaetsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.kognitive_flexibilitaets_weight, 0.0)

    def test_kki_kognitive_flexibilitaets_charta_aggregates_charta_signal(self) -> None:
        charta = build_kognitive_flexibilitaets_charta(charta_id="charta-399-signal")
        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-399-signal-stability-lane",))
        self.assertEqual(charta.kognitiv_flexibel_norm_ids, ("charta-399-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-399-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #400 KognitionsVerfassung (Block-Krone ⭐ Issue #400!)
    # ------------------------------------------------------------------

    def test_kki_kognitions_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_kognitions_verfassung(verfassung_id="verfassung-400-stability")
        norm = next(n for n in verfassung.normen if n.geltung is KognitionsVerfassungsGeltung.GESPERRT)
        self.assertEqual(norm.kognitions_verfassungs_typ, KognitionsVerfassungsTyp.SCHUTZ_KOGNITIONSVERFASSUNG)
        self.assertEqual(norm.prozedur, KognitionsVerfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kognitions_verfassungs_tier, 1)

    def test_kki_kognitions_verfassung_builds_kognitionsverfasst_ordnungs_norm(self) -> None:
        verfassung = build_kognitions_verfassung(verfassung_id="verfassung-400-governance")
        norm = next(n for n in verfassung.normen if n.geltung is KognitionsVerfassungsGeltung.KOGNITIONSVERFASST)
        self.assertEqual(norm.kognitions_verfassungs_typ, KognitionsVerfassungsTyp.ORDNUNGS_KOGNITIONSVERFASSUNG)
        self.assertEqual(norm.prozedur, KognitionsVerfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kognitions_verfassungs_weight, 0.0)

    def test_kki_kognitions_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_kognitions_verfassung(verfassung_id="verfassung-400-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is KognitionsVerfassungsGeltung.GRUNDLEGEND_KOGNITIONSVERFASST)
        self.assertEqual(norm.kognitions_verfassungs_typ, KognitionsVerfassungsTyp.SOUVERAENITAETS_KOGNITIONSVERFASSUNG)
        self.assertEqual(norm.prozedur, KognitionsVerfassungsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.kognitions_verfassungs_weight, 0.0)

    def test_kki_kognitions_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_kognitions_verfassung(verfassung_id="verfassung-400-signal")
        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-400-signal-stability-lane",))
        self.assertEqual(verfassung.kognitionsverfasst_norm_ids, ("verfassung-400-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-400-signal-expansion-lane",))


    # ------------------------------------------------------------------
    # #401 MathematikFeld
    # ------------------------------------------------------------------

    def test_kki_mathematik_feld_builds_gesperrt_schutz_norm(self) -> None:
        obj = build_mathematik_feld(feld_id="feld-401-stability")
        norm = next(n for n in obj.normen if n.geltung is MathematikFeldGeltung.GESPERRT)
        self.assertEqual(norm.mathematik_typ, MathematikFeldTyp.SCHUTZ_MATHEMATIK)
        self.assertEqual(norm.prozedur, MathematikFeldProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.mathematik_tier, 1)

    def test_kki_mathematik_feld_builds_mathematisch_ordnungs_norm(self) -> None:
        obj = build_mathematik_feld(feld_id="feld-401-governance")
        norm = next(n for n in obj.normen if n.geltung is MathematikFeldGeltung.MATHEMATISCH)
        self.assertEqual(norm.mathematik_typ, MathematikFeldTyp.ORDNUNGS_MATHEMATIK)
        self.assertEqual(norm.prozedur, MathematikFeldProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.mathematik_weight, 0.0)

    def test_kki_mathematik_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        obj = build_mathematik_feld(feld_id="feld-401-expansion")
        norm = next(n for n in obj.normen if n.geltung is MathematikFeldGeltung.GRUNDLEGEND_MATHEMATISCH)
        self.assertEqual(norm.mathematik_typ, MathematikFeldTyp.SOUVERAENITAETS_MATHEMATIK)
        self.assertEqual(norm.prozedur, MathematikFeldProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.mathematik_weight, 0.0)

    def test_kki_mathematik_feld_aggregates_feld_signal(self) -> None:
        obj = build_mathematik_feld(feld_id="feld-401-signal")
        self.assertEqual(obj.feld_signal.status, "feld-gesperrt")
        self.assertEqual(obj.gesperrt_norm_ids, ("feld-401-signal-stability-lane",))
        self.assertEqual(obj.mathematisch_norm_ids, ("feld-401-signal-governance-lane",))
        self.assertEqual(obj.grundlegend_norm_ids, ("feld-401-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #402 MengenRegister
    # ------------------------------------------------------------------

    def test_kki_mengen_register_builds_gesperrt_schutz_norm(self) -> None:
        obj = build_mengen_register(register_id="register-402-stability")
        norm = next(n for n in obj.normen if n.geltung is MengenRegisterGeltung.GESPERRT)
        self.assertEqual(norm.mengen_typ, MengenRegisterTyp.SCHUTZ_MENGEN)
        self.assertEqual(norm.prozedur, MengenRegisterProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.mengen_tier, 1)

    def test_kki_mengen_register_builds_mengentheoretisch_ordnungs_norm(self) -> None:
        obj = build_mengen_register(register_id="register-402-governance")
        norm = next(n for n in obj.normen if n.geltung is MengenRegisterGeltung.MENGENTHEORETISCH)
        self.assertEqual(norm.mengen_typ, MengenRegisterTyp.ORDNUNGS_MENGEN)
        self.assertEqual(norm.prozedur, MengenRegisterProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.mengen_weight, 0.0)

    def test_kki_mengen_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        obj = build_mengen_register(register_id="register-402-expansion")
        norm = next(n for n in obj.normen if n.geltung is MengenRegisterGeltung.GRUNDLEGEND_MENGENTHEORETISCH)
        self.assertEqual(norm.mengen_typ, MengenRegisterTyp.SOUVERAENITAETS_MENGEN)
        self.assertEqual(norm.prozedur, MengenRegisterProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.mengen_weight, 0.0)

    def test_kki_mengen_register_aggregates_register_signal(self) -> None:
        obj = build_mengen_register(register_id="register-402-signal")
        self.assertEqual(obj.register_signal.status, "register-gesperrt")
        self.assertEqual(obj.gesperrt_norm_ids, ("register-402-signal-stability-lane",))
        self.assertEqual(obj.mengentheoretisch_norm_ids, ("register-402-signal-governance-lane",))
        self.assertEqual(obj.grundlegend_norm_ids, ("register-402-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #403 LogikCharta
    # ------------------------------------------------------------------

    def test_kki_logik_charta_builds_gesperrt_schutz_norm(self) -> None:
        obj = build_logik_charta(charta_id="charta-403-stability")
        norm = next(n for n in obj.normen if n.geltung is LogikChartaGeltung.GESPERRT)
        self.assertEqual(norm.logik_typ, LogikChartaTyp.SCHUTZ_LOGIK)
        self.assertEqual(norm.prozedur, LogikChartaProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.logik_tier, 1)

    def test_kki_logik_charta_builds_logisch_ordnungs_norm(self) -> None:
        obj = build_logik_charta(charta_id="charta-403-governance")
        norm = next(n for n in obj.normen if n.geltung is LogikChartaGeltung.LOGISCH)
        self.assertEqual(norm.logik_typ, LogikChartaTyp.ORDNUNGS_LOGIK)
        self.assertEqual(norm.prozedur, LogikChartaProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.logik_weight, 0.0)

    def test_kki_logik_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        obj = build_logik_charta(charta_id="charta-403-expansion")
        norm = next(n for n in obj.normen if n.geltung is LogikChartaGeltung.GRUNDLEGEND_LOGISCH)
        self.assertEqual(norm.logik_typ, LogikChartaTyp.SOUVERAENITAETS_LOGIK)
        self.assertEqual(norm.prozedur, LogikChartaProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.logik_weight, 0.0)

    def test_kki_logik_charta_aggregates_charta_signal(self) -> None:
        obj = build_logik_charta(charta_id="charta-403-signal")
        self.assertEqual(obj.charta_signal.status, "charta-gesperrt")
        self.assertEqual(obj.gesperrt_norm_ids, ("charta-403-signal-stability-lane",))
        self.assertEqual(obj.logisch_norm_ids, ("charta-403-signal-governance-lane",))
        self.assertEqual(obj.grundlegend_norm_ids, ("charta-403-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #404 WahrscheinlichkeitsKodex
    # ------------------------------------------------------------------

    def test_kki_wahrscheinlichkeits_kodex_builds_gesperrt_schutz_norm(self) -> None:
        obj = build_wahrscheinlichkeits_kodex(kodex_id="kodex-404-stability")
        norm = next(n for n in obj.normen if n.geltung is WahrscheinlichkeitsKodexGeltung.GESPERRT)
        self.assertEqual(norm.wahrscheinlichkeits_typ, WahrscheinlichkeitsKodexTyp.SCHUTZ_WAHRSCHEINLICHKEIT)
        self.assertEqual(norm.prozedur, WahrscheinlichkeitsKodexProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.wahrscheinlichkeits_tier, 1)

    def test_kki_wahrscheinlichkeits_kodex_builds_probabilistisch_ordnungs_norm(self) -> None:
        obj = build_wahrscheinlichkeits_kodex(kodex_id="kodex-404-governance")
        norm = next(n for n in obj.normen if n.geltung is WahrscheinlichkeitsKodexGeltung.PROBABILISTISCH)
        self.assertEqual(norm.wahrscheinlichkeits_typ, WahrscheinlichkeitsKodexTyp.ORDNUNGS_WAHRSCHEINLICHKEIT)
        self.assertEqual(norm.prozedur, WahrscheinlichkeitsKodexProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.wahrscheinlichkeits_weight, 0.0)

    def test_kki_wahrscheinlichkeits_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        obj = build_wahrscheinlichkeits_kodex(kodex_id="kodex-404-expansion")
        norm = next(n for n in obj.normen if n.geltung is WahrscheinlichkeitsKodexGeltung.GRUNDLEGEND_PROBABILISTISCH)
        self.assertEqual(norm.wahrscheinlichkeits_typ, WahrscheinlichkeitsKodexTyp.SOUVERAENITAETS_WAHRSCHEINLICHKEIT)
        self.assertEqual(norm.prozedur, WahrscheinlichkeitsKodexProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.wahrscheinlichkeits_weight, 0.0)

    def test_kki_wahrscheinlichkeits_kodex_aggregates_kodex_signal(self) -> None:
        obj = build_wahrscheinlichkeits_kodex(kodex_id="kodex-404-signal")
        self.assertEqual(obj.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(obj.gesperrt_norm_ids, ("kodex-404-signal-stability-lane",))
        self.assertEqual(obj.probabilistisch_norm_ids, ("kodex-404-signal-governance-lane",))
        self.assertEqual(obj.grundlegend_norm_ids, ("kodex-404-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #405 SpieltheoriePakt
    # ------------------------------------------------------------------

    def test_kki_spieltheorie_pakt_builds_gesperrt_schutz_norm(self) -> None:
        obj = build_spieltheorie_pakt(pakt_id="pakt-405-stability")
        norm = next(n for n in obj.normen if n.geltung is SpieltheoriePaktGeltung.GESPERRT)
        self.assertEqual(norm.spieltheorie_typ, SpieltheoriePaktTyp.SCHUTZ_SPIELTHEORIE)
        self.assertEqual(norm.prozedur, SpieltheoriePaktProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.spieltheorie_tier, 1)

    def test_kki_spieltheorie_pakt_builds_spieltheoretisch_ordnungs_norm(self) -> None:
        obj = build_spieltheorie_pakt(pakt_id="pakt-405-governance")
        norm = next(n for n in obj.normen if n.geltung is SpieltheoriePaktGeltung.SPIELTHEORETISCH)
        self.assertEqual(norm.spieltheorie_typ, SpieltheoriePaktTyp.ORDNUNGS_SPIELTHEORIE)
        self.assertEqual(norm.prozedur, SpieltheoriePaktProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.spieltheorie_weight, 0.0)

    def test_kki_spieltheorie_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        obj = build_spieltheorie_pakt(pakt_id="pakt-405-expansion")
        norm = next(n for n in obj.normen if n.geltung is SpieltheoriePaktGeltung.GRUNDLEGEND_SPIELTHEORETISCH)
        self.assertEqual(norm.spieltheorie_typ, SpieltheoriePaktTyp.SOUVERAENITAETS_SPIELTHEORIE)
        self.assertEqual(norm.prozedur, SpieltheoriePaktProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.spieltheorie_weight, 0.0)

    def test_kki_spieltheorie_pakt_aggregates_pakt_signal(self) -> None:
        obj = build_spieltheorie_pakt(pakt_id="pakt-405-signal")
        self.assertEqual(obj.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(obj.gesperrt_norm_ids, ("pakt-405-signal-stability-lane",))
        self.assertEqual(obj.spieltheoretisch_norm_ids, ("pakt-405-signal-governance-lane",))
        self.assertEqual(obj.grundlegend_norm_ids, ("pakt-405-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #406 GraphenManifest
    # ------------------------------------------------------------------

    def test_kki_graphen_manifest_builds_gesperrt_schutz_norm(self) -> None:
        obj = build_graphen_manifest(manifest_id="manifest-406-stability")
        norm = next(n for n in obj.normen if n.geltung is GraphenManifestGeltung.GESPERRT)
        self.assertEqual(norm.graphen_typ, GraphenManifestTyp.SCHUTZ_GRAPHEN)
        self.assertEqual(norm.prozedur, GraphenManifestProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.graphen_tier, 1)

    def test_kki_graphen_manifest_builds_graphentheoretisch_ordnungs_norm(self) -> None:
        obj = build_graphen_manifest(manifest_id="manifest-406-governance")
        norm = next(n for n in obj.normen if n.geltung is GraphenManifestGeltung.GRAPHENTHEORETISCH)
        self.assertEqual(norm.graphen_typ, GraphenManifestTyp.ORDNUNGS_GRAPHEN)
        self.assertEqual(norm.prozedur, GraphenManifestProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.graphen_weight, 0.0)

    def test_kki_graphen_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        obj = build_graphen_manifest(manifest_id="manifest-406-expansion")
        norm = next(n for n in obj.normen if n.geltung is GraphenManifestGeltung.GRUNDLEGEND_GRAPHENTHEORETISCH)
        self.assertEqual(norm.graphen_typ, GraphenManifestTyp.SOUVERAENITAETS_GRAPHEN)
        self.assertEqual(norm.prozedur, GraphenManifestProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.graphen_weight, 0.0)

    def test_kki_graphen_manifest_aggregates_manifest_signal(self) -> None:
        obj = build_graphen_manifest(manifest_id="manifest-406-signal")
        self.assertEqual(obj.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(obj.gesperrt_norm_ids, ("manifest-406-signal-stability-lane",))
        self.assertEqual(obj.graphentheoretisch_norm_ids, ("manifest-406-signal-governance-lane",))
        self.assertEqual(obj.grundlegend_norm_ids, ("manifest-406-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #407 AlgorithmenSenat
    # ------------------------------------------------------------------

    def test_kki_algorithmen_senat_builds_gesperrt_schutz_norm(self) -> None:
        obj = build_algorithmen_senat(senat_id="senat-407-stability")
        norm = next(n for n in obj.normen if n.geltung is AlgorithmenSenatGeltung.GESPERRT)
        self.assertEqual(norm.algorithmen_typ, AlgorithmenSenatTyp.SCHUTZ_ALGORITHMEN)
        self.assertEqual(norm.prozedur, AlgorithmenSenatProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.algorithmen_tier, 1)

    def test_kki_algorithmen_senat_builds_algorithmisch_ordnungs_norm(self) -> None:
        obj = build_algorithmen_senat(senat_id="senat-407-governance")
        norm = next(n for n in obj.normen if n.geltung is AlgorithmenSenatGeltung.ALGORITHMISCH)
        self.assertEqual(norm.algorithmen_typ, AlgorithmenSenatTyp.ORDNUNGS_ALGORITHMEN)
        self.assertEqual(norm.prozedur, AlgorithmenSenatProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.algorithmen_weight, 0.0)

    def test_kki_algorithmen_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        obj = build_algorithmen_senat(senat_id="senat-407-expansion")
        norm = next(n for n in obj.normen if n.geltung is AlgorithmenSenatGeltung.GRUNDLEGEND_ALGORITHMISCH)
        self.assertEqual(norm.algorithmen_typ, AlgorithmenSenatTyp.SOUVERAENITAETS_ALGORITHMEN)
        self.assertEqual(norm.prozedur, AlgorithmenSenatProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.algorithmen_weight, 0.0)

    def test_kki_algorithmen_senat_aggregates_senat_signal(self) -> None:
        obj = build_algorithmen_senat(senat_id="senat-407-signal")
        self.assertEqual(obj.senat_signal.status, "senat-gesperrt")
        self.assertEqual(obj.gesperrt_norm_ids, ("senat-407-signal-stability-lane",))
        self.assertEqual(obj.algorithmisch_norm_ids, ("senat-407-signal-governance-lane",))
        self.assertEqual(obj.grundlegend_norm_ids, ("senat-407-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #408 GodelNorm (*_norm)
    # ------------------------------------------------------------------

    def test_kki_godel_norm_builds_gesperrt_schutz_eintrag(self) -> None:
        satz = build_godel_norm(norm_id="norm-408-stability")
        eintrag = next(n for n in satz.normen if n.geltung is GodelNormGeltung.GESPERRT)
        self.assertEqual(eintrag.godel_norm_typ, GodelNormTyp.SCHUTZ_GODEL_NORM)
        self.assertEqual(eintrag.prozedur, GodelNormProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.godel_norm_tier, 1)

    def test_kki_godel_norm_builds_godelunvollstaendig_ordnungs_eintrag(self) -> None:
        satz = build_godel_norm(norm_id="norm-408-governance")
        eintrag = next(n for n in satz.normen if n.geltung is GodelNormGeltung.GODELUNVOLLSTAENDIG)
        self.assertEqual(eintrag.godel_norm_typ, GodelNormTyp.ORDNUNGS_GODEL_NORM)
        self.assertEqual(eintrag.prozedur, GodelNormProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.godel_norm_weight, 0.0)

    def test_kki_godel_norm_builds_grundlegend_souveraenitaets_eintrag(self) -> None:
        satz = build_godel_norm(norm_id="norm-408-expansion")
        eintrag = next(n for n in satz.normen if n.geltung is GodelNormGeltung.GRUNDLEGEND_GODELUNVOLLSTAENDIG)
        self.assertEqual(eintrag.godel_norm_typ, GodelNormTyp.SOUVERAENITAETS_GODEL_NORM)
        self.assertEqual(eintrag.prozedur, GodelNormProzedur.PLENARPROTOKOLL)
        self.assertGreater(eintrag.godel_norm_weight, 0.0)

    def test_kki_godel_norm_aggregates_norm_signal(self) -> None:
        satz = build_godel_norm(norm_id="norm-408-signal")
        self.assertEqual(satz.norm_signal.status, "norm-gesperrt")
        self.assertEqual(satz.gesperrt_norm_ids, ("norm-408-signal-stability-lane",))
        self.assertEqual(satz.godelunvollstaendig_norm_ids, ("norm-408-signal-governance-lane",))
        self.assertEqual(satz.grundlegend_norm_ids, ("norm-408-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #409 TopologieCharta
    # ------------------------------------------------------------------

    def test_kki_topologie_charta_builds_gesperrt_schutz_norm(self) -> None:
        obj = build_topologie_charta(charta_id="charta-409-stability")
        norm = next(n for n in obj.normen if n.geltung is TopologieChartaGeltung.GESPERRT)
        self.assertEqual(norm.topologie_typ, TopologieChartaTyp.SCHUTZ_TOPOLOGIE)
        self.assertEqual(norm.prozedur, TopologieChartaProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.topologie_tier, 1)

    def test_kki_topologie_charta_builds_topologisch_ordnungs_norm(self) -> None:
        obj = build_topologie_charta(charta_id="charta-409-governance")
        norm = next(n for n in obj.normen if n.geltung is TopologieChartaGeltung.TOPOLOGISCH)
        self.assertEqual(norm.topologie_typ, TopologieChartaTyp.ORDNUNGS_TOPOLOGIE)
        self.assertEqual(norm.prozedur, TopologieChartaProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.topologie_weight, 0.0)

    def test_kki_topologie_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        obj = build_topologie_charta(charta_id="charta-409-expansion")
        norm = next(n for n in obj.normen if n.geltung is TopologieChartaGeltung.GRUNDLEGEND_TOPOLOGISCH)
        self.assertEqual(norm.topologie_typ, TopologieChartaTyp.SOUVERAENITAETS_TOPOLOGIE)
        self.assertEqual(norm.prozedur, TopologieChartaProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.topologie_weight, 0.0)

    def test_kki_topologie_charta_aggregates_charta_signal(self) -> None:
        obj = build_topologie_charta(charta_id="charta-409-signal")
        self.assertEqual(obj.charta_signal.status, "charta-gesperrt")
        self.assertEqual(obj.gesperrt_norm_ids, ("charta-409-signal-stability-lane",))
        self.assertEqual(obj.topologisch_norm_ids, ("charta-409-signal-governance-lane",))
        self.assertEqual(obj.grundlegend_norm_ids, ("charta-409-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #410 MathematikVerfassung (Block-Krone ⭐)
    # ------------------------------------------------------------------

    def test_kki_mathematik_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        obj = build_mathematik_verfassung(verfassung_id="verfassung-410-stability")
        norm = next(n for n in obj.normen if n.geltung is MathematikVerfassungsGeltung.GESPERRT)
        self.assertEqual(norm.mathematik_verfassungs_typ, MathematikVerfassungsTyp.SCHUTZ_MATHEMATIKVERFASSUNG)
        self.assertEqual(norm.prozedur, MathematikVerfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.mathematik_verfassungs_tier, 1)

    def test_kki_mathematik_verfassung_builds_mathematikverfasst_ordnungs_norm(self) -> None:
        obj = build_mathematik_verfassung(verfassung_id="verfassung-410-governance")
        norm = next(n for n in obj.normen if n.geltung is MathematikVerfassungsGeltung.MATHEMATIKVERFASST)
        self.assertEqual(norm.mathematik_verfassungs_typ, MathematikVerfassungsTyp.ORDNUNGS_MATHEMATIKVERFASSUNG)
        self.assertEqual(norm.prozedur, MathematikVerfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.mathematik_verfassungs_weight, 0.0)

    def test_kki_mathematik_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        obj = build_mathematik_verfassung(verfassung_id="verfassung-410-expansion")
        norm = next(n for n in obj.normen if n.geltung is MathematikVerfassungsGeltung.GRUNDLEGEND_MATHEMATIKVERFASST)
        self.assertEqual(norm.mathematik_verfassungs_typ, MathematikVerfassungsTyp.SOUVERAENITAETS_MATHEMATIKVERFASSUNG)
        self.assertEqual(norm.prozedur, MathematikVerfassungsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.mathematik_verfassungs_weight, 0.0)

    def test_kki_mathematik_verfassung_aggregates_verfassung_signal(self) -> None:
        obj = build_mathematik_verfassung(verfassung_id="verfassung-410-signal")
        self.assertEqual(obj.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(obj.gesperrt_norm_ids, ("verfassung-410-signal-stability-lane",))
        self.assertEqual(obj.mathematikverfasst_norm_ids, ("verfassung-410-signal-governance-lane",))
        self.assertEqual(obj.grundlegend_norm_ids, ("verfassung-410-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #411 EmergenzFeld
    # ------------------------------------------------------------------

    def test_kki_emergenz_feld_builds_gesperrt_schutz_norm(self) -> None:
        feld = build_emergenz_feld(feld_id="feld-411-stability")
        norm = next(n for n in feld.normen if n.geltung is EmergenzFeldGeltung.GESPERRT)
        self.assertEqual(norm.emergenz_typ, EmergenzFeldTyp.SCHUTZ_EMERGENZ)
        self.assertEqual(norm.prozedur, EmergenzFeldProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.emergenz_tier, 1)

    def test_kki_emergenz_feld_builds_emergent_ordnungs_norm(self) -> None:
        feld = build_emergenz_feld(feld_id="feld-411-governance")
        norm = next(n for n in feld.normen if n.geltung is EmergenzFeldGeltung.EMERGENT)
        self.assertEqual(norm.emergenz_typ, EmergenzFeldTyp.ORDNUNGS_EMERGENZ)
        self.assertEqual(norm.prozedur, EmergenzFeldProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.emergenz_weight, 0.0)

    def test_kki_emergenz_feld_builds_grundlegend_souveraenitaets_norm(self) -> None:
        feld = build_emergenz_feld(feld_id="feld-411-expansion")
        norm = next(n for n in feld.normen if n.geltung is EmergenzFeldGeltung.GRUNDLEGEND_EMERGENT)
        self.assertEqual(norm.emergenz_typ, EmergenzFeldTyp.SOUVERAENITAETS_EMERGENZ)
        self.assertEqual(norm.prozedur, EmergenzFeldProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.emergenz_weight, 0.0)

    def test_kki_emergenz_feld_aggregates_feld_signal(self) -> None:
        feld = build_emergenz_feld(feld_id="feld-411-signal")
        self.assertEqual(feld.feld_signal.status, "feld-gesperrt")
        self.assertEqual(feld.gesperrt_norm_ids, ("feld-411-signal-stability-lane",))
        self.assertEqual(feld.emergent_norm_ids, ("feld-411-signal-governance-lane",))
        self.assertEqual(feld.grundlegend_norm_ids, ("feld-411-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #412 DissipativeStrukturenRegister
    # ------------------------------------------------------------------

    def test_kki_dissipative_strukturen_register_builds_gesperrt_schutz_norm(self) -> None:
        reg = build_dissipative_strukturen_register(register_id="register-412-stability")
        norm = next(n for n in reg.normen if n.geltung is DissipativeStrukturenRegisterGeltung.GESPERRT)
        self.assertEqual(norm.dissipation_typ, DissipativeStrukturenRegisterTyp.SCHUTZ_DISSIPATION)
        self.assertEqual(norm.prozedur, DissipativeStrukturenRegisterProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.dissipation_tier, 1)

    def test_kki_dissipative_strukturen_register_builds_dissipativ_ordnungs_norm(self) -> None:
        reg = build_dissipative_strukturen_register(register_id="register-412-governance")
        norm = next(n for n in reg.normen if n.geltung is DissipativeStrukturenRegisterGeltung.DISSIPATIV)
        self.assertEqual(norm.dissipation_typ, DissipativeStrukturenRegisterTyp.ORDNUNGS_DISSIPATION)
        self.assertEqual(norm.prozedur, DissipativeStrukturenRegisterProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.dissipation_weight, 0.0)

    def test_kki_dissipative_strukturen_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        reg = build_dissipative_strukturen_register(register_id="register-412-expansion")
        norm = next(n for n in reg.normen if n.geltung is DissipativeStrukturenRegisterGeltung.GRUNDLEGEND_DISSIPATIV)
        self.assertEqual(norm.dissipation_typ, DissipativeStrukturenRegisterTyp.SOUVERAENITAETS_DISSIPATION)
        self.assertEqual(norm.prozedur, DissipativeStrukturenRegisterProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.dissipation_weight, 0.0)

    def test_kki_dissipative_strukturen_register_aggregates_register_signal(self) -> None:
        reg = build_dissipative_strukturen_register(register_id="register-412-signal")
        self.assertEqual(reg.register_signal.status, "register-gesperrt")
        self.assertEqual(reg.gesperrt_norm_ids, ("register-412-signal-stability-lane",))
        self.assertEqual(reg.dissipativ_norm_ids, ("register-412-signal-governance-lane",))
        self.assertEqual(reg.grundlegend_norm_ids, ("register-412-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #413 KritikalitaetsCharta
    # ------------------------------------------------------------------

    def test_kki_kritikalitaets_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_kritikalitaets_charta(charta_id="charta-413-stability")
        norm = next(n for n in charta.normen if n.geltung is KritikalitaetsChartaGeltung.GESPERRT)
        self.assertEqual(norm.kritikalitaet_typ, KritikalitaetsChartaTyp.SCHUTZ_KRITIKALITAET)
        self.assertEqual(norm.prozedur, KritikalitaetsChartaProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kritikalitaet_tier, 1)

    def test_kki_kritikalitaets_charta_builds_kritisch_ordnungs_norm(self) -> None:
        charta = build_kritikalitaets_charta(charta_id="charta-413-governance")
        norm = next(n for n in charta.normen if n.geltung is KritikalitaetsChartaGeltung.KRITISCH)
        self.assertEqual(norm.kritikalitaet_typ, KritikalitaetsChartaTyp.ORDNUNGS_KRITIKALITAET)
        self.assertEqual(norm.prozedur, KritikalitaetsChartaProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kritikalitaet_weight, 0.0)

    def test_kki_kritikalitaets_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_kritikalitaets_charta(charta_id="charta-413-expansion")
        norm = next(n for n in charta.normen if n.geltung is KritikalitaetsChartaGeltung.GRUNDLEGEND_KRITISCH)
        self.assertEqual(norm.kritikalitaet_typ, KritikalitaetsChartaTyp.SOUVERAENITAETS_KRITIKALITAET)
        self.assertEqual(norm.prozedur, KritikalitaetsChartaProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.kritikalitaet_weight, 0.0)

    def test_kki_kritikalitaets_charta_aggregates_charta_signal(self) -> None:
        charta = build_kritikalitaets_charta(charta_id="charta-413-signal")
        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-413-signal-stability-lane",))
        self.assertEqual(charta.kritisch_norm_ids, ("charta-413-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-413-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #414 FraktalKodex
    # ------------------------------------------------------------------

    def test_kki_fraktal_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_fraktal_kodex(kodex_id="kodex-414-stability")
        norm = next(n for n in kodex.normen if n.geltung is FraktalKodexGeltung.GESPERRT)
        self.assertEqual(norm.fraktal_typ, FraktalKodexTyp.SCHUTZ_FRAKTAL)
        self.assertEqual(norm.prozedur, FraktalKodexProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.fraktal_tier, 1)

    def test_kki_fraktal_kodex_builds_fraktal_ordnungs_norm(self) -> None:
        kodex = build_fraktal_kodex(kodex_id="kodex-414-governance")
        norm = next(n for n in kodex.normen if n.geltung is FraktalKodexGeltung.FRAKTAL)
        self.assertEqual(norm.fraktal_typ, FraktalKodexTyp.ORDNUNGS_FRAKTAL)
        self.assertEqual(norm.prozedur, FraktalKodexProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.fraktal_weight, 0.0)

    def test_kki_fraktal_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_fraktal_kodex(kodex_id="kodex-414-expansion")
        norm = next(n for n in kodex.normen if n.geltung is FraktalKodexGeltung.GRUNDLEGEND_FRAKTAL)
        self.assertEqual(norm.fraktal_typ, FraktalKodexTyp.SOUVERAENITAETS_FRAKTAL)
        self.assertEqual(norm.prozedur, FraktalKodexProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.fraktal_weight, 0.0)

    def test_kki_fraktal_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_fraktal_kodex(kodex_id="kodex-414-signal")
        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-414-signal-stability-lane",))
        self.assertEqual(kodex.fraktal_norm_ids, ("kodex-414-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-414-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #415 ZellulaereAutomatenPakt
    # ------------------------------------------------------------------

    def test_kki_zellulaere_automaten_pakt_builds_gesperrt_schutz_norm(self) -> None:
        pakt = build_zellulaere_automaten_pakt(pakt_id="pakt-415-stability")
        norm = next(n for n in pakt.normen if n.geltung is ZellulaereAutomatenPaktGeltung.GESPERRT)
        self.assertEqual(norm.zellulaerautomat_typ, ZellulaereAutomatenPaktTyp.SCHUTZ_ZELLULAERAUTOMAT)
        self.assertEqual(norm.prozedur, ZellulaereAutomatenPaktProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.zellulaerautomat_tier, 1)

    def test_kki_zellulaere_automaten_pakt_builds_zellulaerautomat_ordnungs_norm(self) -> None:
        pakt = build_zellulaere_automaten_pakt(pakt_id="pakt-415-governance")
        norm = next(n for n in pakt.normen if n.geltung is ZellulaereAutomatenPaktGeltung.ZELLULAERAUTOMAT)
        self.assertEqual(norm.zellulaerautomat_typ, ZellulaereAutomatenPaktTyp.ORDNUNGS_ZELLULAERAUTOMAT)
        self.assertEqual(norm.prozedur, ZellulaereAutomatenPaktProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.zellulaerautomat_weight, 0.0)

    def test_kki_zellulaere_automaten_pakt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        pakt = build_zellulaere_automaten_pakt(pakt_id="pakt-415-expansion")
        norm = next(n for n in pakt.normen if n.geltung is ZellulaereAutomatenPaktGeltung.GRUNDLEGEND_ZELLULAERAUTOMAT)
        self.assertEqual(norm.zellulaerautomat_typ, ZellulaereAutomatenPaktTyp.SOUVERAENITAETS_ZELLULAERAUTOMAT)
        self.assertEqual(norm.prozedur, ZellulaereAutomatenPaktProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.zellulaerautomat_weight, 0.0)

    def test_kki_zellulaere_automaten_pakt_aggregates_pakt_signal(self) -> None:
        pakt = build_zellulaere_automaten_pakt(pakt_id="pakt-415-signal")
        self.assertEqual(pakt.pakt_signal.status, "pakt-gesperrt")
        self.assertEqual(pakt.gesperrt_norm_ids, ("pakt-415-signal-stability-lane",))
        self.assertEqual(pakt.zellulaerautomat_norm_ids, ("pakt-415-signal-governance-lane",))
        self.assertEqual(pakt.grundlegend_norm_ids, ("pakt-415-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #416 FitnessLandschaftManifest
    # ------------------------------------------------------------------

    def test_kki_fitness_landschaft_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_fitness_landschaft_manifest(manifest_id="manifest-416-stability")
        norm = next(n for n in manifest.normen if n.geltung is FitnessLandschaftManifestGeltung.GESPERRT)
        self.assertEqual(norm.fitness_landschaft_typ, FitnessLandschaftManifestTyp.SCHUTZ_FITNESS_LANDSCHAFT)
        self.assertEqual(norm.prozedur, FitnessLandschaftManifestProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.fitness_landschaft_tier, 1)

    def test_kki_fitness_landschaft_manifest_builds_fitnesskartiert_ordnungs_norm(self) -> None:
        manifest = build_fitness_landschaft_manifest(manifest_id="manifest-416-governance")
        norm = next(n for n in manifest.normen if n.geltung is FitnessLandschaftManifestGeltung.FITNESSKARTIERT)
        self.assertEqual(norm.fitness_landschaft_typ, FitnessLandschaftManifestTyp.ORDNUNGS_FITNESS_LANDSCHAFT)
        self.assertEqual(norm.prozedur, FitnessLandschaftManifestProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.fitness_landschaft_weight, 0.0)

    def test_kki_fitness_landschaft_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_fitness_landschaft_manifest(manifest_id="manifest-416-expansion")
        norm = next(n for n in manifest.normen if n.geltung is FitnessLandschaftManifestGeltung.GRUNDLEGEND_FITNESSKARTIERT)
        self.assertEqual(norm.fitness_landschaft_typ, FitnessLandschaftManifestTyp.SOUVERAENITAETS_FITNESS_LANDSCHAFT)
        self.assertEqual(norm.prozedur, FitnessLandschaftManifestProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.fitness_landschaft_weight, 0.0)

    def test_kki_fitness_landschaft_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_fitness_landschaft_manifest(manifest_id="manifest-416-signal")
        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-416-signal-stability-lane",))
        self.assertEqual(manifest.fitnesskartiert_norm_ids, ("manifest-416-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-416-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #417 AdaptiveSystemeSenat
    # ------------------------------------------------------------------

    def test_kki_adaptive_systeme_senat_builds_gesperrt_schutz_norm(self) -> None:
        senat = build_adaptive_systeme_senat(senat_id="senat-417-stability")
        norm = next(n for n in senat.normen if n.geltung is AdaptiveSystemeSenatGeltung.GESPERRT)
        self.assertEqual(norm.adaptiv_typ, AdaptiveSystemeSenatTyp.SCHUTZ_ADAPTIV)
        self.assertEqual(norm.prozedur, AdaptiveSystemeSenatProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.adaptiv_tier, 1)

    def test_kki_adaptive_systeme_senat_builds_adaptiv_ordnungs_norm(self) -> None:
        senat = build_adaptive_systeme_senat(senat_id="senat-417-governance")
        norm = next(n for n in senat.normen if n.geltung is AdaptiveSystemeSenatGeltung.ADAPTIV)
        self.assertEqual(norm.adaptiv_typ, AdaptiveSystemeSenatTyp.ORDNUNGS_ADAPTIV)
        self.assertEqual(norm.prozedur, AdaptiveSystemeSenatProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.adaptiv_weight, 0.0)

    def test_kki_adaptive_systeme_senat_builds_grundlegend_souveraenitaets_norm(self) -> None:
        senat = build_adaptive_systeme_senat(senat_id="senat-417-expansion")
        norm = next(n for n in senat.normen if n.geltung is AdaptiveSystemeSenatGeltung.GRUNDLEGEND_ADAPTIV)
        self.assertEqual(norm.adaptiv_typ, AdaptiveSystemeSenatTyp.SOUVERAENITAETS_ADAPTIV)
        self.assertEqual(norm.prozedur, AdaptiveSystemeSenatProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.adaptiv_weight, 0.0)

    def test_kki_adaptive_systeme_senat_aggregates_senat_signal(self) -> None:
        senat = build_adaptive_systeme_senat(senat_id="senat-417-signal")
        self.assertEqual(senat.senat_signal.status, "senat-gesperrt")
        self.assertEqual(senat.gesperrt_norm_ids, ("senat-417-signal-stability-lane",))
        self.assertEqual(senat.adaptiv_norm_ids, ("senat-417-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_norm_ids, ("senat-417-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #418 SynergetikNorm (*_norm)
    # ------------------------------------------------------------------

    def test_kki_synergetik_norm_builds_gesperrt_schutz_eintrag(self) -> None:
        satz = build_synergetik_norm(norm_id="norm-418-stability")
        eintrag = next(n for n in satz.normen if n.geltung is SynergetikNormGeltung.GESPERRT)
        self.assertEqual(eintrag.synergetik_norm_typ, SynergetikNormTyp.SCHUTZ_SYNERGETIK_NORM)
        self.assertEqual(eintrag.prozedur, SynergetikNormProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.synergetik_norm_tier, 1)

    def test_kki_synergetik_norm_builds_synergetisch_ordnungs_eintrag(self) -> None:
        satz = build_synergetik_norm(norm_id="norm-418-governance")
        eintrag = next(n for n in satz.normen if n.geltung is SynergetikNormGeltung.SYNERGETISCH)
        self.assertEqual(eintrag.synergetik_norm_typ, SynergetikNormTyp.ORDNUNGS_SYNERGETIK_NORM)
        self.assertEqual(eintrag.prozedur, SynergetikNormProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.synergetik_norm_weight, 0.0)

    def test_kki_synergetik_norm_builds_grundlegend_souveraenitaets_eintrag(self) -> None:
        satz = build_synergetik_norm(norm_id="norm-418-expansion")
        eintrag = next(n for n in satz.normen if n.geltung is SynergetikNormGeltung.GRUNDLEGEND_SYNERGETISCH)
        self.assertEqual(eintrag.synergetik_norm_typ, SynergetikNormTyp.SOUVERAENITAETS_SYNERGETIK_NORM)
        self.assertEqual(eintrag.prozedur, SynergetikNormProzedur.PLENARPROTOKOLL)
        self.assertGreater(eintrag.synergetik_norm_weight, 0.0)

    def test_kki_synergetik_norm_aggregates_norm_signal(self) -> None:
        satz = build_synergetik_norm(norm_id="norm-418-signal")
        self.assertEqual(satz.norm_signal.status, "norm-gesperrt")
        self.assertEqual(satz.gesperrt_norm_ids, ("norm-418-signal-stability-lane",))
        self.assertEqual(satz.synergetisch_norm_ids, ("norm-418-signal-governance-lane",))
        self.assertEqual(satz.grundlegend_norm_ids, ("norm-418-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #419 KuenstlichesLebenCharta
    # ------------------------------------------------------------------

    def test_kki_kuenstliches_leben_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_kuenstliches_leben_charta(charta_id="charta-419-stability")
        norm = next(n for n in charta.normen if n.geltung is KuenstlichesLebenChartaGeltung.GESPERRT)
        self.assertEqual(norm.kuenstliches_leben_typ, KuenstlichesLebenChartaTyp.SCHUTZ_KUENSTLICHES_LEBEN)
        self.assertEqual(norm.prozedur, KuenstlichesLebenChartaProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kuenstliches_leben_tier, 1)

    def test_kki_kuenstliches_leben_charta_builds_alife_ordnungs_norm(self) -> None:
        charta = build_kuenstliches_leben_charta(charta_id="charta-419-governance")
        norm = next(n for n in charta.normen if n.geltung is KuenstlichesLebenChartaGeltung.ALIFE)
        self.assertEqual(norm.kuenstliches_leben_typ, KuenstlichesLebenChartaTyp.ORDNUNGS_KUENSTLICHES_LEBEN)
        self.assertEqual(norm.prozedur, KuenstlichesLebenChartaProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kuenstliches_leben_weight, 0.0)

    def test_kki_kuenstliches_leben_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_kuenstliches_leben_charta(charta_id="charta-419-expansion")
        norm = next(n for n in charta.normen if n.geltung is KuenstlichesLebenChartaGeltung.GRUNDLEGEND_ALIFE)
        self.assertEqual(norm.kuenstliches_leben_typ, KuenstlichesLebenChartaTyp.SOUVERAENITAETS_KUENSTLICHES_LEBEN)
        self.assertEqual(norm.prozedur, KuenstlichesLebenChartaProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.kuenstliches_leben_weight, 0.0)

    def test_kki_kuenstliches_leben_charta_aggregates_charta_signal(self) -> None:
        charta = build_kuenstliches_leben_charta(charta_id="charta-419-signal")
        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-419-signal-stability-lane",))
        self.assertEqual(charta.alife_norm_ids, ("charta-419-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-419-signal-expansion-lane",))

    # ------------------------------------------------------------------
    # #420 KomplexeSystemeVerfassung (Block-Krone ⭐)
    # ------------------------------------------------------------------

    def test_kki_komplexe_systeme_verfassung_builds_gesperrt_schutz_norm(self) -> None:
        verfassung = build_komplexe_systeme_verfassung(verfassung_id="verfassung-420-stability")
        norm = next(n for n in verfassung.normen if n.geltung is KomplexeSystemeVerfassungsGeltung.GESPERRT)
        self.assertEqual(norm.komplexe_systeme_verfassungs_typ, KomplexeSystemeVerfassungsTyp.SCHUTZ_KOMPLEXSYSTEMVERFASSUNG)
        self.assertEqual(norm.prozedur, KomplexeSystemeVerfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.komplexe_systeme_verfassungs_tier, 1)

    def test_kki_komplexe_systeme_verfassung_builds_komplexsystemverfasst_ordnungs_norm(self) -> None:
        verfassung = build_komplexe_systeme_verfassung(verfassung_id="verfassung-420-governance")
        norm = next(n for n in verfassung.normen if n.geltung is KomplexeSystemeVerfassungsGeltung.KOMPLEXSYSTEMVERFASST)
        self.assertEqual(norm.komplexe_systeme_verfassungs_typ, KomplexeSystemeVerfassungsTyp.ORDNUNGS_KOMPLEXSYSTEMVERFASSUNG)
        self.assertEqual(norm.prozedur, KomplexeSystemeVerfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.komplexe_systeme_verfassungs_weight, 0.0)

    def test_kki_komplexe_systeme_verfassung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        verfassung = build_komplexe_systeme_verfassung(verfassung_id="verfassung-420-expansion")
        norm = next(n for n in verfassung.normen if n.geltung is KomplexeSystemeVerfassungsGeltung.GRUNDLEGEND_KOMPLEXSYSTEMVERFASST)
        self.assertEqual(norm.komplexe_systeme_verfassungs_typ, KomplexeSystemeVerfassungsTyp.SOUVERAENITAETS_KOMPLEXSYSTEMVERFASSUNG)
        self.assertEqual(norm.prozedur, KomplexeSystemeVerfassungsProzedur.PLENARPROTOKOLL)
        self.assertGreater(norm.komplexe_systeme_verfassungs_weight, 0.0)

    def test_kki_komplexe_systeme_verfassung_aggregates_verfassung_signal(self) -> None:
        verfassung = build_komplexe_systeme_verfassung(verfassung_id="verfassung-420-signal")
        self.assertEqual(verfassung.verfassung_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_norm_ids, ("verfassung-420-signal-stability-lane",))
        self.assertEqual(verfassung.komplexsystemverfasst_norm_ids, ("verfassung-420-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_norm_ids, ("verfassung-420-signal-expansion-lane",))


if __name__ == "__main__":
    unittest.main()
