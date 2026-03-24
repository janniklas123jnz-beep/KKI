"""KKI build-phase foundation package."""

from .data_models import (
    CoreState,
    EvidenceRecord,
    PersistenceRecord,
    TransferEnvelope,
    core_state_for_runtime,
    transfer_envelope_for_state,
)
from .change_windows import ChangeWindow, ChangeWindowEntry, ChangeWindowStatus, open_change_window
from .benchmark_harness import (
    BenchmarkCase,
    BenchmarkCaseResult,
    BenchmarkHarness,
    BenchmarkReleaseMode,
    benchmark_case_matrix,
    run_benchmark_harness,
)
from .autonomy_governor import AutonomyAssignment, AutonomyDecision, AutonomyGovernor, build_autonomy_governor
from .capacity_planner import CapacityLane, CapacityPlanEntry, CapacityPlanner, CapacityWindow, build_capacity_planner
from .continuous_readiness import (
    ContinuousReadinessCycle,
    ContinuousReadinessIteration,
    ContinuousReadinessStatus,
    build_continuous_readiness_cycle,
)
from .convergence_simulator import (
    ConvergenceProjection,
    ConvergenceSimulator,
    ConvergenceStatus,
    build_convergence_simulator,
)
from .exception_register import ExceptionCase, ExceptionKind, ExceptionRegister, ExceptionSeverity, build_exception_register
from .executive_watchtower import (
    ExecutiveOrder,
    ExecutiveOrderMode,
    ExecutiveWatchStatus,
    ExecutiveWatchtower,
    build_executive_watchtower,
)
from .strategy_council import (
    StrategyCouncil,
    StrategyCouncilStatus,
    StrategyEscalationMandate,
    StrategyLane,
    StrategyMandate,
    StrategyPriority,
    build_strategy_council,
)
from .mandate_card_deck import (
    MandateCard,
    MandateCardDeck,
    MandateExecutionScope,
    MandateReviewCadence,
    build_mandate_card_deck,
)
from .portfolio_radar import (
    PortfolioConcentration,
    PortfolioExposure,
    PortfolioOperatingSpread,
    PortfolioRadar,
    PortfolioRadarEntry,
    build_portfolio_radar,
)
from .scenario_chancery import (
    ScenarioChancery,
    ScenarioOfficeMode,
    ScenarioOfficeStatus,
    ScenarioOption,
    build_scenario_chancery,
)
from .course_corrector import (
    CourseCorrector,
    CourseCorrectionAction,
    CourseCorrectionDirective,
    CourseCorrectionStatus,
    build_course_corrector,
)
from .mandate_memory_store import (
    MandateMemoryRecord,
    MandateMemoryStatus,
    MandateMemoryStore,
    build_mandate_memory_store,
)
from .guideline_compass import (
    CompassStatus,
    GuidelineCompass,
    GuidelinePrinciple,
    GuidelineVector,
    NavigationConstraint,
    build_guideline_compass,
)
from .intervention_charter import (
    CharterStatus,
    InterventionCharter,
    InterventionClause,
    InterventionRight,
    ReleaseThreshold,
    StopCondition,
    build_intervention_charter,
)
from .program_senate import (
    ProgramSenate,
    SenateBalanceStatus,
    SenatePriority,
    SenateResolution,
    SenateSeat,
    build_program_senate,
)
from .directive_consensus import (
    ConsensusDirective,
    ConsensusDirectiveStatus,
    ConsensusDirectiveType,
    ConsensusMandate,
    DirectiveConsensus,
    build_directive_consensus,
)
from .decision_archive import (
    ArchiveEntry,
    ArchiveRetention,
    ArchiveStatus,
    DecisionArchive,
    build_decision_archive,
)
from .execution_cabinet import (
    CabinetExecutionMode,
    CabinetOrder,
    CabinetRole,
    CabinetStatus,
    ExecutionCabinet,
    build_execution_cabinet,
)
from .delegation_matrix import (
    DelegationEntry,
    DelegationLane,
    DelegationMatrix,
    DelegationMode,
    DelegationStatus,
    build_delegation_matrix,
)
from .veto_sluice import (
    RecallPath,
    ReleasePath,
    SluiceStatus,
    VetoChannel,
    VetoSluice,
    VetoStop,
    build_veto_sluice,
)
from .consensus_diplomacy import (
    ConsensusDiplomacy,
    DiplomacyChannel,
    DiplomacyPath,
    DiplomacyPosture,
    DiplomacyStatus,
    build_consensus_diplomacy,
)
from .leitstern_doctrine import (
    DoctrineClause,
    DoctrinePrinciple,
    DoctrineScope,
    DoctrineStatus,
    LeitsternDoctrine,
    build_leitstern_doctrine,
)
from .missions_collegium import (
    CollegiumLane,
    CollegiumMandate,
    CollegiumSeat,
    CollegiumStatus,
    MissionsCollegium,
    build_missions_collegium,
)
from .priority_conclave import (
    ConclaveLane,
    ConclaveMotion,
    ConclavePriority,
    ConclaveStatus,
    PriorityConclave,
    build_priority_conclave,
)
from .course_contract import (
    ContractClause,
    ContractCommitment,
    ContractParty,
    ContractStatus,
    CourseContract,
    build_course_contract,
)
from .leitstern_codex import (
    CodexAxis,
    CodexCanon,
    CodexSection,
    CodexStatus,
    LeitsternCodex,
    build_leitstern_codex,
)
from .kodex_register import (
    KodexRegister,
    KodexRegisterEntry,
    RegisterRetention,
    RegisterTier,
    build_kodex_register,
)
from .satzungs_rat import (
    RatBench,
    RatInterpretation,
    RatStatus,
    SatzungsRat,
    SatzungsRatArticle,
    build_satzungs_rat,
)
from .mandats_konvent import (
    KonventEbene,
    KonventMandat,
    KonventStatus,
    MandatsKonvent,
    MandatsLinie,
    build_mandats_konvent,
)
from .normen_tribunal import (
    NormenTribunal,
    TribunalFall,
    TribunalKammer,
    TribunalUrteil,
    TribunalVerfahren,
    build_normen_tribunal,
)
from .verfassungs_senat import (
    SenatsBeschluss,
    SenatsFraktion,
    SenatsSitzung,
    SenatsMandat,
    VerfassungsSenat,
    build_verfassungs_senat,
)
from .grundrechts_charta import (
    ChartaArtikel,
    ChartaGeltung,
    ChartaKapitel,
    ChartaVerfahren,
    GrundrechtsCharta,
    build_grundrechts_charta,
)
from .souveraenitaets_akt import (
    AktKlausel,
    AktProzedur,
    AktSektion,
    AktStatus,
    SouveraenitaetsAkt,
    build_souveraenitaets_akt,
)
from .ordnungs_manifest import (
    ManifestAbschnitt,
    ManifestGeltung,
    ManifestKapitel,
    ManifestVerfahren,
    OrdnungsManifest,
    build_ordnungs_manifest,
)
from .leitordnung import (
    Leitordnung,
    OrdnungsKraft,
    OrdnungsNorm,
    OrdnungsRang,
    OrdnungsTyp,
    build_leitordnung,
)
from .autoritaets_dekret import (
    AutoritaetsDekret,
    DekretGeltung,
    DekretKlausel,
    DekretProzedur,
    DekretSektion,
    build_autoritaets_dekret,
)
from .rechts_fundament import (
    FundamentKraft,
    FundamentPfeiler,
    FundamentSaeule,
    FundamentVerfahren,
    RechtsFundament,
    build_rechts_fundament,
)
from .grundsatz_register import (
    GrundsatzRegister,
    RegisterEintrag,
    RegisterKategorie,
    RegisterProzedur,
    RegisterStatus,
    build_grundsatz_register,
)
from .prinzipien_kodex import (
    PrinzipienKlasse,
    PrinzipienKodex,
    PrinzipienProzedur,
    PrinzipienSatz,
    PrinzipienStatus,
    build_prinzipien_kodex,
)
from .werte_charta import (
    WerteArtikel,
    WerteCharta,
    WerteProzedur,
    WerteStatus,
    WerteTyp,
    build_werte_charta,
)
from .leitbild_konvent import (
    KonventBeschluss,
    KonventProzedur,
    LeitbildAusrichtung,
    LeitbildKonvent,
    LeitbildResolution,
    build_leitbild_konvent,
)
from .missions_verfassung import (
    MissionsArtikel,
    MissionsRang,
    MissionsVerfassung,
    VerfassungsProzedur,
    VerfassungsStatus,
    build_missions_verfassung,
)
from .zweck_manifest import (
    ManifestGeltung,
    ManifestProzedur,
    ZweckDimension,
    ZweckKlausel,
    ZweckManifest,
    build_zweck_manifest,
)
from .leitstern_konstitution import (
    KonstitutionsArtikel,
    KonstitutionsEbene,
    KonstitutionsProzedur,
    KonstitutionsRang,
    LeitsternKonstitution,
    build_leitstern_konstitution,
)
from .verfassungs_grundgesetz import (
    GrundgesetzGeltung,
    GrundgesetzParagraph,
    GrundgesetzProzedur,
    GrundgesetzTitel,
    VerfassungsGrundgesetz,
    build_verfassungs_grundgesetz,
)
from .staats_ordnung import (
    StaatsEbene,
    StaatsGeltung,
    StaatsNorm,
    StaatsOrdnung,
    StaatsProzedur,
    build_staats_ordnung,
)
from .rechts_kodex import (
    KodexKlasse,
    KodexNorm,
    KodexProzedur,
    KodexStatus,
    RechtsKodex,
    build_rechts_kodex,
)
from .unions_akt import (
    UnionsAkt,
    UnionsGeltung,
    UnionsNorm,
    UnionsProzedur,
    UnionsTyp,
    build_unions_akt,
)
from .foederal_vertrag import (
    FoederalGeltung,
    FoederalNorm,
    FoederalProzedur,
    FoederalTyp,
    FoederalVertrag,
    build_foederal_vertrag,
)
from .bundes_charta import (
    BundesCharta,
    BundesGeltung,
    BundesNorm,
    BundesProzedur,
    BundesRang,
    build_bundes_charta,
)
from .hoheits_manifest import (
    HoheitsGeltung,
    HoheitsGrad,
    HoheitsManifest,
    HoheitsNorm,
    HoheitsProzedur,
    build_hoheits_manifest,
)
from .supremats_register import (
    SuprematsGeltung,
    SuprematsKlasse,
    SuprematsNorm,
    SuprematsProzedur,
    SuprematsRegister,
    build_supremats_register,
)
from .grundrechts_senat import (
    GrundrechtsSenat,
    SenatGeltung,
    SenatNorm,
    SenatProzedur,
    SenatRang,
    build_grundrechts_senat,
)
from .verfassungs_kodex import (
    VerfassungsKodex,
    VerfassungsKodexGeltung,
    VerfassungsKodexNorm,
    VerfassungsKodexProzedur,
    VerfassungsKodexRang,
    build_verfassungs_kodex,
)
from .weltordnungs_prinzip import (
    WeltordnungsEbene,
    WeltordnungsGeltung,
    WeltordnungsNorm,
    WeltordnungsPrinzip,
    WeltordnungsProzedur,
    build_weltordnungs_prinzip,
)
from .voelkerrechts_kodex_kosmopolitik import (
    VoelkerrechtsGeltung,
    VoelkerrechtsKlasse,
    VoelkerrechtsKodex,
    VoelkerrechtsNorm,
    VoelkerrechtsProzedur,
    build_voelkerrechts_kodex,
)
from .diplomatie_charta import (
    DiplomatieCharta,
    DiplomatieGeltung,
    DiplomatieNorm,
    DiplomatieProzedur,
    DiplomatieRang,
    build_diplomatie_charta,
)
from .allianz_vertrag import (
    AllianzGeltung,
    AllianzNorm,
    AllianzProzedur,
    AllianzTyp,
    AllianzVertrag,
    build_allianz_vertrag,
)
from .kooperations_manifest import (
    KooperationsGeltung,
    KooperationsGrad,
    KooperationsManifest,
    KooperationsNorm,
    KooperationsProzedur,
    build_kooperations_manifest,
)
from .solidaritaets_pakt import (
    SolidaritaetsGeltung,
    SolidaritaetsNorm,
    SolidaritaetsPakt,
    SolidaritaetsProzedur,
    SolidaritaetsTyp,
    build_solidaritaets_pakt,
)
from .universalrechts_register import (
    UniversalrechtsGeltung,
    UniversalrechtsNorm,
    UniversalrechtsProzedur,
    UniversalrechtsRang,
    UniversalrechtsRegister,
    build_universalrechts_register,
)
from .kosmos_norm import (
    KosmosEbene,
    KosmosGeltung,
    KosmosNorm,
    KosmosNormEintrag,
    KosmosProzedur,
    build_kosmos_norm,
)
from .weltgeist_senat import (
    WeltgeistGeltung,
    WeltgeistProzedur,
    WeltgeistRang,
    WeltgeistSenat,
    WeltgeistSitz,
    build_weltgeist_senat,
)
from .universal_kodex import (
    UniversalKodex,
    UniversalKodexGeltung,
    UniversalKodexKlasse,
    UniversalKodexNorm,
    UniversalKodexProzedur,
    build_universal_kodex,
)
from .ursprungs_charta import (
    UrsprungsCharta,
    UrsprungsGeltung,
    UrsprungsNorm,
    UrsprungsProzedur,
    UrsprungsTyp,
    build_ursprungs_charta,
)
from .schoepfungs_vertrag import (
    SchoepfungsGeltung,
    SchoepfungsGrad,
    SchoepfungsNorm,
    SchoepfungsProzedur,
    SchoepfungsVertrag,
    build_schoepfungs_vertrag,
)
from .erbe_register import (
    ErbeGeltung,
    ErbeKlasse,
    ErbeNorm,
    ErbeProzedur,
    ErbeRegister,
    build_erbe_register,
)
from .zivilisations_pakt import (
    ZivilisationsGeltung,
    ZivilisationsNorm,
    ZivilisationsPakt,
    ZivilisationsProzedur,
    ZivilisationsTyp,
    build_zivilisations_pakt,
)
from .kulturgut_kodex import (
    KulturgutGeltung,
    KulturgutKodex,
    KulturgutNorm,
    KulturgutProzedur,
    KulturgutRang,
    build_kulturgut_kodex,
)
from .wissens_manifest import (
    WissensGeltung,
    WissensGrad,
    WissensManifest,
    WissensNorm,
    WissensProzedur,
    build_wissens_manifest,
)
from .gedaechtnis_senat import (
    GedaechtnisGeltung,
    GedaechtnisNorm,
    GedaechtnisProzedur,
    GedaechtnisRang,
    GedaechtnisSenat,
    build_gedaechtnis_senat,
)
from .weisheits_norm import (
    WeisheitsEbene,
    WeisheitsGeltung,
    WeisheitsNorm,
    WeisheitsNormEintrag,
    WeisheitsProzedur,
    build_weisheits_norm,
)
from .erkenntnis_charta import (
    ErkenntnisCharta,
    ErkenntnisGeltung,
    ErkenntnisNorm,
    ErkenntnisProzedur,
    ErkenntnisTyp,
    build_erkenntnis_charta,
)
from .transzendenz_kodex import (
    TranszendenzEbene,
    TranszendenzGeltung,
    TranszendenzKodex,
    TranszendenzNorm,
    TranszendenzProzedur,
    build_transzendenz_kodex,
)
from .ursprungs_axiom import (
    AxiomGeltung,
    AxiomProzedur,
    AxiomRang,
    UrsprungsAxiom,
    UrsprungsAxiomEintrag,
    build_ursprungs_axiom,
)
from .seins_charta import (
    SeinsCharta,
    SeinsGeltung,
    SeinsNorm,
    SeinsProzedur,
    SeinsTyp,
    build_seins_charta,
)
from .wirklichkeits_kodex import (
    WirklichkeitsEbene,
    WirklichkeitsGeltung,
    WirklichkeitsKodex,
    WirklichkeitsNorm,
    WirklichkeitsProzedur,
    build_wirklichkeits_kodex,
)
from .kausalitaets_register import (
    KausalitaetsGeltung,
    KausalitaetsNorm,
    KausalitaetsProzedur,
    KausalitaetsRang,
    KausalitaetsRegister,
    build_kausalitaets_register,
)
from .kosmos_ordnung import (
    KosmosOrdnung,
    KosmosOrdnungsGeltung,
    KosmosOrdnungsNorm,
    KosmosOrdnungsProzedur,
    KosmosOrdnungsTyp,
    build_kosmos_ordnung,
)
from .harmonie_pakt import (
    HarmonieGeltung,
    HarmonieNorm,
    HarmoniePakt,
    HarmonieProzedur,
    HarmonieTyp,
    build_harmonie_pakt,
)
from .einheits_senat import (
    EinheitsGeltung,
    EinheitsNorm,
    EinheitsProzedur,
    EinheitsSenat,
    EinheitsTyp,
    build_einheits_senat,
)
from .ewigkeits_norm import (
    EwigkeitsEintrag,
    EwigkeitsGeltung,
    EwigkeitsNorm,
    EwigkeitsProzedur,
    EwigkeitsTyp,
    build_ewigkeits_norm,
)
from .kosmos_ewigkeit import (
    KosmosEwigkeit,
    KosmosEwigkeitsGeltung,
    KosmosEwigkeitsNormEintrag,
    KosmosEwigkeitsProzedur,
    KosmosEwigkeitsRang,
    build_kosmos_ewigkeit,
)
from .absolut_charta import (
    AbsolutCharta,
    AbsolutGeltung,
    AbsolutNorm,
    AbsolutProzedur,
    AbsolutTyp,
    build_absolut_charta,
)
from .kosmos_verfassung import (
    KosmosVerfassung,
    KosmosVerfassungsGeltung,
    KosmosVerfassungsNorm,
    KosmosVerfassungsProzedur,
    KosmosVerfassungsTyp,
    build_kosmos_verfassung,
)
from .quanten_feld import (
    QuantenFeld,
    QuantenFeldGeltung,
    QuantenFeldNorm,
    QuantenFeldProzedur,
    QuantenFeldTyp,
    build_quanten_feld,
)
from .dimensions_register import (
    DimensionsGeltung,
    DimensionsNorm,
    DimensionsProzedur,
    DimensionsRang,
    DimensionsRegister,
    build_dimensions_register,
)
from .wellen_charta import (
    WellenCharta,
    WellenGeltung,
    WellenNorm,
    WellenProzedur,
    WellenTyp,
    build_wellen_charta,
)
from .superpositions_kodex import (
    SuperpositionsGeltung,
    SuperpositionsKodex,
    SuperpositionsNorm,
    SuperpositionsProzedur,
    SuperpositionsTyp,
    build_superpositions_kodex,
)
from .verschraenkungs_pakt import (
    VerschraenkunsGeltung,
    VerschraenkunsNorm,
    VerschraenkunsPakt,
    VerschraenkunsProzedur,
    VerschraenkunsTyp,
    build_verschraenkungs_pakt,
)
from .kollaps_manifest import (
    KollapsGeltung,
    KollapsManifest,
    KollapsNorm,
    KollapsProzedur,
    KollapsTyp,
    build_kollaps_manifest,
)
from .quanten_senat import (
    QuantenSenat,
    QuantenSenatGeltung,
    QuantenSenatNorm,
    QuantenSenatProzedur,
    QuantenSenatTyp,
    build_quanten_senat,
)
from .planck_norm import (
    PlanckGeltung,
    PlanckNorm,
    PlanckNormEintrag,
    PlanckProzedur,
    PlanckTyp,
    build_planck_norm,
)
from .stringtheorie_charta import (
    StringtheorieCharta,
    StringtheorieGeltung,
    StringtheorieNorm,
    StringtheorieProzedur,
    StringtheorieTyp,
    build_stringtheorie_charta,
)
from .quanten_verfassung import (
    QuantenVerfassung,
    QuantenVerfassungsGeltung,
    QuantenVerfassungsNorm,
    QuantenVerfassungsProzedur,
    QuantenVerfassungsTyp,
    build_quanten_verfassung,
)
from .relativitaets_feld import (
    RelativitaetsFeld,
    RelativitaetsGeltung,
    RelativitaetsNorm,
    RelativitaetsProzedur,
    RelativitaetsTyp,
    build_relativitaets_feld,
)
from .raumzeit_register import (
    RaumzeitGeltung,
    RaumzeitNorm,
    RaumzeitProzedur,
    RaumzeitRang,
    RaumzeitRegister,
    build_raumzeit_register,
)
from .lichtgeschwindigkeits_charta import (
    LichtgeschwindigkeitsCharta,
    LichtgeschwindigkeitsGeltung,
    LichtgeschwindigkeitsNorm,
    LichtgeschwindigkeitsProzedur,
    LichtgeschwindigkeitsTyp,
    build_lichtgeschwindigkeits_charta,
)
from .gravitations_kodex import (
    GravitationsGeltung,
    GravitationsKodex,
    GravitationsNorm,
    GravitationsProzedur,
    GravitationsTyp,
    build_gravitations_kodex,
)
from .kruemmungs_pakt import (
    KruemmungsGeltung,
    KruemmungsNorm,
    KruemmungsPakt,
    KruemmungsProzedur,
    KruemmungsTyp,
    build_kruemmungs_pakt,
)
from .singularitaets_manifest import (
    SingularitaetsGeltung,
    SingularitaetsManifest,
    SingularitaetsNorm,
    SingularitaetsProzedur,
    SingularitaetsTyp,
    build_singularitaets_manifest,
)
from .schwarzes_loch_senat import (
    SchwarzeLoechSenat,
    SchwarzsLochGeltung,
    SchwarzsLochNorm,
    SchwarzsLochProzedur,
    SchwarzsLochTyp,
    build_schwarzes_loch_senat,
)
from .ereignishorizont_norm import (
    EreignishorizontGeltung,
    EreignishorizontNorm,
    EreignishorizontNormEintrag,
    EreignishorizontProzedur,
    EreignishorizontTyp,
    build_ereignishorizont_norm,
)
from .zeitdilatations_charta import (
    ZeitdilatationsCharta,
    ZeitdilatationsGeltung,
    ZeitdilatationsNorm,
    ZeitdilatationsProzedur,
    ZeitdilatationsTyp,
    build_zeitdilatations_charta,
)
from .relativitaets_verfassung import (
    RelativitaetsGeltung,
    RelativitaetsNorm,
    RelativitaetsProzedur,
    RelativitaetsTyp,
    RelativitaetsVerfassung,
    build_relativitaets_verfassung,
)
from .thermodynamik_feld import (
    ThermodynamikFeld,
    ThermodynamikGeltung,
    ThermodynamikNorm,
    ThermodynamikProzedur,
    ThermodynamikTyp,
    build_thermodynamik_feld,
)
from .entropie_register import (
    EntropieGeltung,
    EntropieNorm,
    EntropieRegister,
    EntropieProzedur,
    EntropieTyp,
    build_entropie_register,
)
from .waerme_charta import (
    WaermeCharta,
    WaermeGeltung,
    WaermeNorm,
    WaermeProzedur,
    WaermeTyp,
    build_waerme_charta,
)
from .energieerhaltungs_kodex import (
    EnergieerhaltungsGeltung,
    EnergieerhaltungsKodex,
    EnergieerhaltungsNorm,
    EnergieerhaltungsProzedur,
    EnergieerhaltungsTyp,
    build_energieerhaltungs_kodex,
)
from .gleichgewichts_pakt import (
    GleichgewichtsGeltung,
    GleichgewichtsNorm,
    GleichgewichtsPakt,
    GleichgewichtsProzedur,
    GleichgewichtsTyp,
    build_gleichgewichts_pakt,
)
from .carnot_manifest import (
    CarnotGeltung,
    CarnotManifest,
    CarnotNorm,
    CarnotProzedur,
    CarnotTyp,
    build_carnot_manifest,
)
from .boltzmann_senat import (
    BoltzmannGeltung,
    BoltzmannNorm,
    BoltzmannSenat,
    BoltzmannProzedur,
    BoltzmannTyp,
    build_boltzmann_senat,
)
from .entropie_norm import (
    EntropieNormEintrag,
    EntropieNormGeltung,
    EntropieNormProzedur,
    EntropieNormSatz,
    EntropieNormTyp,
    build_entropie_norm,
)
from .waermestrahlung_charta import (
    WaermestrahlungsCharta,
    WaermestrahlungsGeltung,
    WaermestrahlungsNorm,
    WaermestrahlungsProzedur,
    WaermestrahlungsTyp,
    build_waermestrahlung_charta,
)
from .thermodynamik_verfassung import (
    ThermodynamikVerfassung,
    ThermoverfassungsGeltung,
    ThermoverfassungsNorm,
    ThermoverfassungsProzedur,
    ThermoverfassungsTyp,
    build_thermodynamik_verfassung,
)
from .elektromagnetik_feld import (
    ElektromagnetikFeld,
    ElektromagnetikGeltung,
    ElektromagnetikNorm,
    ElektromagnetikProzedur,
    ElektromagnetikTyp,
    build_elektromagnetik_feld,
)
from .ladungs_register import (
    LadungsGeltung,
    LadungsNorm,
    LadungsProzedur,
    LadungsRegister,
    LadungsTyp,
    build_ladungs_register,
)
from .maxwell_charta import (
    MaxwellCharta,
    MaxwellGeltung,
    MaxwellNorm,
    MaxwellProzedur,
    MaxwellTyp,
    build_maxwell_charta,
)
from .induktions_kodex import (
    InduktionsGeltung,
    InduktionsKodex,
    InduktionsNorm,
    InduktionsProzedur,
    InduktionsTyp,
    build_induktions_kodex,
)
from .wellenausbreitung_pakt import (
    WellenausbreitungsGeltung,
    WellenausbreitungsNorm,
    WellenausbreitungsPakt,
    WellenausbreitungsProzedur,
    WellenausbreitungsTyp,
    build_wellenausbreitung_pakt,
)
from .lichtgeschwindigkeits_manifest import (
    LichtgeschwindigkeitsGeltung,
    LichtgeschwindigkeitsManifest,
    LichtgeschwindigkeitsNorm,
    LichtgeschwindigkeitsProzedur,
    LichtgeschwindigkeitsTyp,
    build_lichtgeschwindigkeits_manifest,
)
from .spektral_senat import (
    SpektralGeltung,
    SpektralNorm,
    SpektralProzedur,
    SpektralSenat,
    SpektralTyp,
    build_spektral_senat,
)
from .photon_norm import (
    PhotonNormEintrag,
    PhotonNormGeltung,
    PhotonNormProzedur,
    PhotonNormSatz,
    PhotonNormTyp,
    build_photon_norm,
)
from .photoeffekt_charta import (
    PhotoeffektCharta,
    PhotoeffektGeltung,
    PhotoeffektNorm,
    PhotoeffektProzedur,
    PhotoeffektTyp,
    build_photoeffekt_charta,
)
from .elektromagnetik_verfassung import (
    ElektromagnetikVerfassung,
    ElektroverfassungsGeltung,
    ElektroverfassungsNorm,
    ElektroverfassungsProzedur,
    ElektroverfassungsTyp,
    build_elektromagnetik_verfassung,
)
from .kernphysik_feld import (
    KernphysikFeld,
    KernphysikGeltung,
    KernphysikNorm,
    KernphysikProzedur,
    KernphysikTyp,
    build_kernphysik_feld,
)
from .nukleon_register import (
    NukleonGeltung,
    NukleonNorm,
    NukleonProzedur,
    NukleonRegister,
    NukleonTyp,
    build_nukleon_register,
)
from .stark_charta import (
    StarkCharta,
    StarkGeltung,
    StarkNorm,
    StarkProzedur,
    StarkTyp,
    build_stark_charta,
)
from .schwach_kodex import (
    SchwachGeltung,
    SchwachKodex,
    SchwachNorm,
    SchwachProzedur,
    SchwachTyp,
    build_schwach_kodex,
)
from .kernspaltungs_pakt import (
    KernspaltungsGeltung,
    KernspaltungsNorm,
    KernspaltungsPakt,
    KernspaltungsProzedur,
    KernspaltungsTyp,
    build_kernspaltungs_pakt,
)
from .kernfusions_manifest import (
    KernfusionsGeltung,
    KernfusionsManifest,
    KernfusionsNorm,
    KernfusionsProzedur,
    KernfusionsTyp,
    build_kernfusions_manifest,
)
from .radioaktivitaets_senat import (
    RadioaktivitaetsGeltung,
    RadioaktivitaetsNorm,
    RadioaktivitaetsProzedur,
    RadioaktivitaetsSenat,
    RadioaktivitaetsTyp,
    build_radioaktivitaets_senat,
)
from .zerfalls_norm import (
    ZerfallsNormEintrag,
    ZerfallsNormGeltung,
    ZerfallsNormProzedur,
    ZerfallsNormSatz,
    ZerfallsNormTyp,
    build_zerfalls_norm,
)
from .nuklear_charta import (
    NuklearCharta,
    NuklearChartaGeltung,
    NuklearChartaNorm,
    NuklearChartaProzedur,
    NuklearChartaTyp,
    build_nuklear_charta,
)
from .kernphysik_verfassung import (
    KernphysikVerfassung,
    KernphysikVerfassungsGeltung,
    KernphysikVerfassungsNorm,
    KernphysikVerfassungsProzedur,
    KernphysikVerfassungsTyp,
    build_kernphysik_verfassung,
)
from .teilchen_feld import (
    TeilchenFeld,
    TeilchenGeltung,
    TeilchenNorm,
    TeilchenProzedur,
    TeilchenTyp,
    build_teilchen_feld,
)
from .quark_register import (
    QuarkGeltung,
    QuarkNorm,
    QuarkProzedur,
    QuarkRegister,
    QuarkTyp,
    build_quark_register,
)
from .lepton_charta import (
    LeptonCharta,
    LeptonGeltung,
    LeptonNorm,
    LeptonProzedur,
    LeptonTyp,
    build_lepton_charta,
)
from .gluon_kodex import (
    GluonGeltung,
    GluonKodex,
    GluonNorm,
    GluonProzedur,
    GluonTyp,
    build_gluon_kodex,
)
from .eichboson_pakt import (
    EichbosonGeltung,
    EichbosonNorm,
    EichbosonPakt,
    EichbosonProzedur,
    EichbosonTyp,
    build_eichboson_pakt,
)
from .higgs_manifest import (
    HiggsGeltung,
    HiggsManifest,
    HiggsNorm,
    HiggsProzedur,
    HiggsTyp,
    build_higgs_manifest,
)
from .symmetriebrechungs_senat import (
    SymmetriebrechungsGeltung,
    SymmetriebrechungsNorm,
    SymmetriebrechungsProzedur,
    SymmetriebrechungsSenat,
    SymmetriebrechungsTyp,
    build_symmetriebrechungs_senat,
)
from .feynman_norm import (
    FeynmanNormEintrag,
    FeynmanNormGeltung,
    FeynmanNormProzedur,
    FeynmanNormSatz,
    FeynmanNormTyp,
    build_feynman_norm,
)
from .standardmodell_charta import (
    StandardmodellCharta,
    StandardmodellGeltung,
    StandardmodellNorm,
    StandardmodellProzedur,
    StandardmodellTyp,
    build_standardmodell_charta,
)
from .teilchenphysik_verfassung import (
    TeilchenphysikGeltung,
    TeilchenphysikNorm,
    TeilchenphysikProzedur,
    TeilchenphysikTyp,
    TeilchenphysikVerfassung,
    build_teilchenphysik_verfassung,
)
from .kosmologie_feld import (
    KosmologieFeld,
    KosmologieGeltung,
    KosmologieNorm,
    KosmologieProzedur,
    KosmologieTyp,
    build_kosmologie_feld,
)
from .urknall_register import (
    UrknallGeltung,
    UrknallNorm,
    UrknallProzedur,
    UrknallRegister,
    UrknallTyp,
    build_urknall_register,
)
from .inflation_charta import (
    InflationCharta,
    InflationGeltung,
    InflationNorm,
    InflationProzedur,
    InflationTyp,
    build_inflation_charta,
)
from .dunkle_materie_kodex import (
    DunkleMaterieGeltung,
    DunkleMaterieKodex,
    DunkleMaterieNorm,
    DunkleMaterieProzedue,
    DunkleMaterieTyp,
    build_dunkle_materie_kodex,
)
from .dunkle_energie_pakt import (
    DunkleEnergieGeltung,
    DunkleEnergieNorm,
    DunkleEnergiePakt,
    DunkleEnergieProzedur,
    DunkleEnergieTyp,
    build_dunkle_energie_pakt,
)
from .cmb_manifest import (
    CmbGeltung,
    CmbManifest,
    CmbNorm,
    CmbProzedur,
    CmbTyp,
    build_cmb_manifest,
)
from .strukturbildungs_senat import (
    StrukturbildungsGeltung,
    StrukturbildungsNorm,
    StrukturbildungsProzedur,
    StrukturbildungsSenat,
    StrukturbildungsTyp,
    build_strukturbildungs_senat,
)
from .expansion_norm import (
    ExpansionNormEintrag,
    ExpansionNormGeltung,
    ExpansionNormProzedur,
    ExpansionNormSatz,
    ExpansionNormTyp,
    build_expansion_norm,
)
from .hubble_charta import (
    HubbleCharta,
    HubbleGeltung,
    HubbleNorm,
    HubbleProzedur,
    HubbleTyp,
    build_hubble_charta,
)
from .kosmologie_verfassung import (
    KosmologieVerfassung,
    KosmologieVerfassungsGeltung,
    KosmologieVerfassungsNorm,
    KosmologieVerfassungsProzedur,
    KosmologieVerfassungsTyp,
    build_kosmologie_verfassung,
)
from .astrophysik_feld import (
    AstrophysikFeld,
    AstrophysikGeltung,
    AstrophysikNorm,
    AstrophysikProzedur,
    AstrophysikTyp,
    build_astrophysik_feld,
)
from .protostellar_register import (
    ProtostellarGeltung,
    ProtostellarNorm,
    ProtostellarProzedur,
    ProtostellarRegister,
    ProtostellarTyp,
    build_protostellar_register,
)
from .hauptreihen_charta import (
    HauptreihenchartaCharta,
    HauptreihenchartaGeltung,
    HauptreihenchartaNorm,
    HauptreihenchartaProzedur,
    HauptreihenchartaTyp,
    build_hauptreihen_charta,
)
from .fusionsreaktor_kodex import (
    FusionsreaktorGeltung,
    FusionsreaktorKodex,
    FusionsreaktorNorm,
    FusionsreaktorProzedur,
    FusionsreaktorTyp,
    build_fusionsreaktor_kodex,
)
from .roter_riese_pakt import (
    RoterRieseGeltung,
    RoterRieseNorm,
    RoterRiesePakt,
    RoterRieseProzedur,
    RoterRieseTyp,
    build_roter_riese_pakt,
)
from .supernova_manifest import (
    SupernovaGeltung,
    SupernovaManifest,
    SupernovaNorm,
    SupernovaProzedur,
    SupernovaTyp,
    build_supernova_manifest,
)
from .neutronenstern_senat import (
    NeutronensternGeltung,
    NeutronensternNorm,
    NeutronensternProzedur,
    NeutronensternSenat,
    NeutronensternTyp,
    build_neutronenstern_senat,
)
from .schwarzes_loch_norm import (
    SchwarzerLochNormEintrag,
    SchwarzerLochNormGeltung,
    SchwarzerLochNormProzedur,
    SchwarzerLochNormSatz,
    SchwarzerLochNormTyp,
    build_schwarzes_loch_norm,
)
from .hertzsprung_russell_charta import (
    HertzsprungRussellCharta,
    HertzsprungRussellGeltung,
    HertzsprungRussellNorm,
    HertzsprungRussellProzedur,
    HertzsprungRussellTyp,
    build_hertzsprung_russell_charta,
)
from .astrophysik_verfassung import (
    AstrophysikVerfassung,
    AstrophysikVerfassungsGeltung,
    AstrophysikVerfassungsNorm,
    AstrophysikVerfassungsProzedur,
    AstrophysikVerfassungsTyp,
    build_astrophysik_verfassung,
)
from .festkoerper_feld import (
    FestkoerperFeld,
    FestkoerperGeltung,
    FestkoerperNorm,
    FestkoerperProzedur,
    FestkoerperTyp,
    build_festkoerper_feld,
)
from .kristallgitter_register import (
    KristallgitterRegister,
    KristallgitterGeltung,
    KristallgitterNorm,
    KristallgitterProzedur,
    KristallgitterTyp,
    build_kristallgitter_register,
)
from .bandstruktur_charta import (
    BandstrukturCharta,
    BandstrukturGeltung,
    BandstrukturNorm,
    BandstrukturProzedur,
    BandstrukturTyp,
    build_bandstruktur_charta,
)
from .halbleiter_kodex import (
    HalbleiterKodex,
    HalbleiterGeltung,
    HalbleiterNorm,
    HalbleiterProzedur,
    HalbleiterTyp,
    build_halbleiter_kodex,
)
from .supraleitung_pakt import (
    SupraleitungPakt,
    SupraleitungGeltung,
    SupraleitungNorm,
    SupraleitungProzedur,
    SupraleitungTyp,
    build_supraleitung_pakt,
)
from .quanten_hall_manifest import (
    QuantenHallManifest,
    QuantenHallGeltung,
    QuantenHallNorm,
    QuantenHallProzedur,
    QuantenHallTyp,
    build_quanten_hall_manifest,
)
from .phonon_senat import (
    PhononSenat,
    PhononGeltung,
    PhononNorm,
    PhononProzedur,
    PhononTyp,
    build_phonon_senat,
)
from .fermi_norm import (
    FermiNormSatz,
    FermiNormEintrag,
    FermiNormGeltung,
    FermiNormProzedur,
    FermiNormTyp,
    build_fermi_norm,
)
from .bose_einstein_charta import (
    BoseEinsteinCharta,
    BoseEinsteinGeltung,
    BoseEinsteinNorm,
    BoseEinsteinProzedur,
    BoseEinsteinTyp,
    build_bose_einstein_charta,
)
from .festkoerper_verfassung import (
    FestkoerperVerfassung,
    FestkoerperVerfassungsGeltung,
    FestkoerperVerfassungsNorm,
    FestkoerperVerfassungsProzedur,
    FestkoerperVerfassungsTyp,
    build_festkoerper_verfassung,
)
from .plasma_feld import (
    PlasmaFeld,
    PlasmaGeltung,
    PlasmaNorm,
    PlasmaProzedur,
    PlasmaTyp,
    build_plasma_feld,
)
from .magnetohydrodynamik_register import (
    MagnetohydrodynamikGeltung,
    MagnetohydrodynamikNorm,
    MagnetohydrodynamikProzedur,
    MagnetohydrodynamikRegister,
    MagnetohydrodynamikTyp,
    build_magnetohydrodynamik_register,
)
from .debye_abschirmung_charta import (
    DebyeAbschirmungCharta,
    DebyeAbschirmungGeltung,
    DebyeAbschirmungNorm,
    DebyeAbschirmungProzedur,
    DebyeAbschirmungTyp,
    build_debye_abschirmung_charta,
)
from .alfven_wellen_kodex import (
    AlfvenWellenGeltung,
    AlfvenWellenKodex,
    AlfvenWellenNorm,
    AlfvenWellenProzedur,
    AlfvenWellenTyp,
    build_alfven_wellen_kodex,
)
from .z_pinch_pakt import (
    ZPinchGeltung,
    ZPinchNorm,
    ZPinchPakt,
    ZPinchProzedur,
    ZPinchTyp,
    build_z_pinch_pakt,
)
from .tokamak_manifest import (
    TokamakGeltung,
    TokamakManifest,
    TokamakNorm,
    TokamakProzedur,
    TokamakTyp,
    build_tokamak_manifest,
)
from .traegheitsfusion_senat import (
    TraegheitsfusionGeltung,
    TraegheitsfusionNorm,
    TraegheitsfusionProzedur,
    TraegheitsfusionSenat,
    TraegheitsfusionTyp,
    build_traegheitsfusion_senat,
)
from .plasmawellen_norm import (
    PlasmaWellenNormEintrag,
    PlasmaWellenNormGeltung,
    PlasmaWellenNormProzedur,
    PlasmaWellenNormSatz,
    PlasmaWellenNormTyp,
    build_plasmawellen_norm,
)
from .kernfusion_charta import (
    KernfusionCharta,
    KernfusionGeltung,
    KernfusionNorm,
    KernfusionProzedur,
    KernfusionTyp,
    build_kernfusion_charta,
)
from .plasma_verfassung import (
    PlasmaVerfassung,
    PlasmaVerfassungsGeltung,
    PlasmaVerfassungsNorm,
    PlasmaVerfassungsProzedur,
    PlasmaVerfassungsTyp,
    build_plasma_verfassung,
)
from .lorenz_attraktor_feld import (
    LorenzAttraktorFeld,
    LorenzAttraktorGeltung,
    LorenzAttraktorNorm,
    LorenzAttraktorProzedur,
    LorenzAttraktorTyp,
    build_lorenz_attraktor_feld,
)
from .bifurkations_register import (
    BifurkationsGeltung,
    BifurkationsNorm,
    BifurkationsProzedur,
    BifurkationsRegister,
    BifurkationsTyp,
    build_bifurkations_register,
)
from .lyapunov_kodex import (
    LyapunovGeltung,
    LyapunovKodex,
    LyapunovNorm,
    LyapunovProzedur,
    LyapunovTyp,
    build_lyapunov_kodex,
)
from .fraktal_charta import (
    FraktalCharta,
    FraktalGeltung,
    FraktalNorm,
    FraktalProzedur,
    FraktalTyp,
    build_fraktal_charta,
)
from .strange_attraktor_pakt import (
    StrangeAttraktorGeltung,
    StrangeAttraktorNorm,
    StrangeAttraktorPakt,
    StrangeAttraktorProzedur,
    StrangeAttraktorTyp,
    build_strange_attraktor_pakt,
)
from .emergenz_senat import (
    EmergenzGeltung,
    EmergenzNorm,
    EmergenzProzedur,
    EmergenzSenat,
    EmergenzTyp,
    build_emergenz_senat,
)
from .perkolations_norm import (
    PerkolationsNormEintrag,
    PerkolationsNormGeltung,
    PerkolationsNormProzedur,
    PerkolationsNormSatz,
    PerkolationsNormTyp,
    build_perkolations_norm,
)
from .komplexitaets_charta import (
    KomplexitaetsCharta,
    KomplexitaetsGeltung,
    KomplexitaetsNorm,
    KomplexitaetsProzedur,
    KomplexitaetsTyp,
    build_komplexitaets_charta,
)
from .adaptiv_schwarm_kodex import (
    AdaptivSchwarmGeltung,
    AdaptivSchwarmKodex,
    AdaptivSchwarmNorm,
    AdaptivSchwarmProzedur,
    AdaptivSchwarmTyp,
    build_adaptiv_schwarm_kodex,
)
from .chaos_verfassung import (
    ChaosVerfassung,
    ChaosVerfassungsGeltung,
    ChaosVerfassungsNorm,
    ChaosVerfassungsProzedur,
    ChaosVerfassungsTyp,
    build_chaos_verfassung,
)
from .shannon_entropie_feld import (
    ShannonEntropieFeld,
    ShannonEntropieGeltung,
    ShannonEntropieNorm,
    ShannonEntropieProzedur,
    ShannonEntropieTyp,
    build_shannon_entropie_feld,
)
from .kanalkapazitaet_register import (
    KanalkapazitaetGeltung,
    KanalkapazitaetNorm,
    KanalkapazitaetProzedur,
    KanalkapazitaetRegister,
    KanalkapazitaetTyp,
    build_kanalkapazitaet_register,
)
from .quanten_bit_kodex import (
    QuantenBitGeltung,
    QuantenBitKodex,
    QuantenBitNorm,
    QuantenBitProzedur,
    QuantenBitTyp,
    build_quanten_bit_kodex,
)
from .verschraenkung_charta import (
    VerschraenkungCharta,
    VerschraenkungGeltung,
    VerschraenkungNorm,
    VerschraenkungProzedur,
    VerschraenkungTyp,
    build_verschraenkung_charta,
)
from .quantenfehler_pakt import (
    QuantenfehlerGeltung,
    QuantenfehlerNorm,
    QuantenfehlerPakt,
    QuantenfehlerProzedur,
    QuantenfehlerTyp,
    build_quantenfehler_pakt,
)
from .quantenkrypto_senat import (
    QuantenkryptoGeltung,
    QuantenkryptoNorm,
    QuantenkryptoProzedur,
    QuantenkryptoSenat,
    QuantenkryptoTyp,
    build_quantenkrypto_senat,
)
from .holographisches_prinzip_norm import (
    HolographischesPrinzipNormEintrag,
    HolographischesPrinzipNormGeltung,
    HolographischesPrinzipNormProzedur,
    HolographischesPrinzipNormSatz,
    HolographischesPrinzipNormTyp,
    build_holographisches_prinzip_norm,
)
from .landauer_manifest import (
    LandauerGeltung,
    LandauerManifest,
    LandauerNorm,
    LandauerProzedur,
    LandauerTyp,
    build_landauer_manifest,
)
from .no_cloning_kodex import (
    NoCloningGeltung,
    NoCloningKodex,
    NoCloningNorm,
    NoCloningProzedur,
    NoCloningTyp,
    build_no_cloning_kodex,
)
from .quanteninformation_verfassung import (
    QuanteninformationsVerfassung,
    QuanteninformationsVerfassungsGeltung,
    QuanteninformationsVerfassungsNorm,
    QuanteninformationsVerfassungsProzedur,
    QuanteninformationsVerfassungsTyp,
    build_quanteninformations_verfassung,
)
from .biophysik_feld import (
    BiophysikFeld,
    BiophysikGeltung,
    BiophysikNorm,
    BiophysikProzedur,
    BiophysikTyp,
    build_biophysik_feld,
)
from .dna_replikation_register import (
    DnaReplikationGeltung,
    DnaReplikationNorm,
    DnaReplikationProzedur,
    DnaReplikationRegister,
    DnaReplikationTyp,
    build_dna_replikation_register,
)
from .proteinfaltung_charta import (
    ProteinfaltungCharta,
    ProteinfaltungGeltung,
    ProteinfaltungNorm,
    ProteinfaltungProzedur,
    ProteinfaltungTyp,
    build_proteinfaltung_charta,
)
from .hodgkin_huxley_kodex import (
    HodgkinHuxleyGeltung,
    HodgkinHuxleyKodex,
    HodgkinHuxleyNorm,
    HodgkinHuxleyProzedur,
    HodgkinHuxleyTyp,
    build_hodgkin_huxley_kodex,
)
from .synaptische_plastizitaet_pakt import (
    SynaptischePlastizitaetGeltung,
    SynaptischePlastizitaetNorm,
    SynaptischePlastizitaetPakt,
    SynaptischePlastizitaetProzedur,
    SynaptischePlastizitaetTyp,
    build_synaptische_plastizitaet_pakt,
)
from .evolution_manifest import (
    EvolutionGeltung,
    EvolutionManifest,
    EvolutionNorm,
    EvolutionProzedur,
    EvolutionTyp,
    build_evolution_manifest,
)
from .homoostase_senat import (
    HomoostaseGeltung,
    HomoostaseNorm,
    HomoostaseSenat,
    HomoostaseTyp,
    HomoostasProzedur,
    build_homoostase_senat,
)
from .lotka_volterra_norm import (
    LotkaVolterraNormEintrag,
    LotkaVolterraNormGeltung,
    LotkaVolterraNormProzedur,
    LotkaVolterraNormSatz,
    LotkaVolterraNormTyp,
    build_lotka_volterra_norm,
)
from .morphogenese_charta import (
    MorphogeneseCharta,
    MorphogeneseGeltung,
    MorphogeneseNorm,
    MorphogeneseProzedur,
    MorphogeneseTyp,
    build_morphogenese_charta,
)
from .systembiologie_verfassung import (
    SystembiologieVerfassung,
    SystembiologieVerfassungsGeltung,
    SystembiologieVerfassungsNorm,
    SystembiologieVerfassungsProzedur,
    SystembiologieVerfassungsTyp,
    build_systembiologie_verfassung,
)
from .kognitions_feld import (
    KognitionsFeld,
    KognitionsGeltung,
    KognitionsNorm,
    KognitionsProzedur,
    KognitionsTyp,
    build_kognitions_feld,
)
from .arbeitsgedaechtnis_register import (
    ArbeitsgedaechtnisGeltung,
    ArbeitsgedaechtnisNorm,
    ArbeitsgedaechtnisRegister,
    ArbeitsgedaechtnisTyp,
    ArbeitsgedaechtnispProzedur,
    build_arbeitsgedaechtnis_register,
)
from .aufmerksamkeits_charta import (
    AufmerksamkeitsCharta,
    AufmerksamkeitsGeltung,
    AufmerksamkeitsNorm,
    AufmerksamkeitsProzedur,
    AufmerksamkeitsTyp,
    build_aufmerksamkeits_charta,
)
from .entscheidungs_kodex import (
    EntscheidungsGeltung,
    EntscheidungsKodex,
    EntscheidungsNorm,
    EntscheidungsProzedur,
    EntscheidungsTyp,
    build_entscheidungs_kodex,
)
from .gedaechtnis_konsolidierungs_pakt import (
    GedaechtnisKonsolidierungsGeltung,
    GedaechtnisKonsolidierungsNorm,
    GedaechtnisKonsolidierungsPakt,
    GedaechtnisKonsolidierungsProzedur,
    GedaechtnisKonsolidierungsTyp,
    build_gedaechtnis_konsolidierungs_pakt,
)
from .sprachverarbeitungs_manifest import (
    SprachverarbeitungsGeltung,
    SprachverarbeitungsManifest,
    SprachverarbeitungsNorm,
    SprachverarbeitungsProzedur,
    SprachverarbeitungsTyp,
    build_sprachverarbeitungs_manifest,
)
from .bewusstseins_senat import (
    BewusstseinsGeltung,
    BewusstseinsNorm,
    BewusstseinsSenat,
    BewusstseinsTyp,
    BewusstseinsProzedur,
    build_bewusstseins_senat,
)
from .metakognitions_norm import (
    MetakognitionsNormEintrag,
    MetakognitionsNormGeltung,
    MetakognitionsNormProzedur,
    MetakognitionsNormSatz,
    MetakognitionsNormTyp,
    build_metakognitions_norm,
)
from .kognitive_flexibilitaets_charta import (
    KognitiveFlexibilitaetsCharta,
    KognitiveFlexibilitaetsGeltung,
    KognitiveFlexibilitaetsNorm,
    KognitiveFlexibilitaetsProzedur,
    KognitiveFlexibilitaetsTyp,
    build_kognitive_flexibilitaets_charta,
)
from .kognitions_verfassung import (
    KognitionsVerfassung,
    KognitionsVerfassungsGeltung,
    KognitionsVerfassungsNorm,
    KognitionsVerfassungsProzedur,
    KognitionsVerfassungsTyp,
    build_kognitions_verfassung,
)
from .mathematik_feld import (
    MathematikFeldGeltung,
    MathematikFeldNorm,
    MathematikFeldProzedur,
    MathematikFeldTyp,
    MathematikFeld,
    build_mathematik_feld,
)
from .mengen_register import (
    MengenRegisterGeltung,
    MengenRegisterNorm,
    MengenRegisterProzedur,
    MengenRegisterTyp,
    MengenRegister,
    build_mengen_register,
)
from .logik_charta import (
    LogikChartaGeltung,
    LogikChartaNorm,
    LogikChartaProzedur,
    LogikChartaTyp,
    LogikCharta,
    build_logik_charta,
)
from .wahrscheinlichkeits_kodex import (
    WahrscheinlichkeitsKodexGeltung,
    WahrscheinlichkeitsKodexNorm,
    WahrscheinlichkeitsKodexProzedur,
    WahrscheinlichkeitsKodexTyp,
    WahrscheinlichkeitsKodex,
    build_wahrscheinlichkeits_kodex,
)
from .spieltheorie_pakt import (
    SpieltheoriePaktGeltung,
    SpieltheoriePaktNorm,
    SpieltheoriePaktProzedur,
    SpieltheoriePaktTyp,
    SpieltheoriePakt,
    build_spieltheorie_pakt,
)
from .graphen_manifest import (
    GraphenManifestGeltung,
    GraphenManifestNorm,
    GraphenManifestProzedur,
    GraphenManifestTyp,
    GraphenManifest,
    build_graphen_manifest,
)
from .algorithmen_senat import (
    AlgorithmenSenatGeltung,
    AlgorithmenSenatNorm,
    AlgorithmenSenatProzedur,
    AlgorithmenSenatTyp,
    AlgorithmenSenat,
    build_algorithmen_senat,
)
from .godel_norm import (
    GodelNormGeltung,
    GodelNormEintrag,
    GodelNormProzedur,
    GodelNormTyp,
    GodelNormSatz,
    build_godel_norm,
)
from .topologie_charta import (
    TopologieChartaGeltung,
    TopologieChartaNorm,
    TopologieChartaProzedur,
    TopologieChartaTyp,
    TopologieCharta,
    build_topologie_charta,
)
from .mathematik_verfassung import (
    MathematikVerfassungsGeltung,
    MathematikVerfassungsNorm,
    MathematikVerfassungsProzedur,
    MathematikVerfassungsTyp,
    MathematikVerfassung,
    build_mathematik_verfassung,
)
# --- Block #411–#420 Komplexe Systeme & Emergenz ---
from .emergenz_feld import (
    EmergenzFeldGeltung,
    EmergenzFeldNorm,
    EmergenzFeldProzedur,
    EmergenzFeldTyp,
    EmergenzFeld,
    build_emergenz_feld,
)
from .dissipative_strukturen_register import (
    DissipativeStrukturenRegisterGeltung,
    DissipativeStrukturenRegisterNorm,
    DissipativeStrukturenRegisterProzedur,
    DissipativeStrukturenRegisterTyp,
    DissipativeStrukturenRegister,
    build_dissipative_strukturen_register,
)
from .kritikalitaets_charta import (
    KritikalitaetsChartaGeltung,
    KritikalitaetsChartaNorm,
    KritikalitaetsChartaProzedur,
    KritikalitaetsChartaTyp,
    KritikalitaetsCharta,
    build_kritikalitaets_charta,
)
from .fraktal_kodex import (
    FraktalKodexGeltung,
    FraktalKodexNorm,
    FraktalKodexProzedur,
    FraktalKodexTyp,
    FraktalKodex,
    build_fraktal_kodex,
)
from .zellulaere_automaten_pakt import (
    ZellulaereAutomatenPaktGeltung,
    ZellulaereAutomatenPaktNorm,
    ZellulaereAutomatenPaktProzedur,
    ZellulaereAutomatenPaktTyp,
    ZellulaereAutomatenPakt,
    build_zellulaere_automaten_pakt,
)
from .fitness_landschaft_manifest import (
    FitnessLandschaftManifestGeltung,
    FitnessLandschaftManifestNorm,
    FitnessLandschaftManifestProzedur,
    FitnessLandschaftManifestTyp,
    FitnessLandschaftManifest,
    build_fitness_landschaft_manifest,
)
from .adaptive_systeme_senat import (
    AdaptiveSystemeSenatGeltung,
    AdaptiveSystemeSenatNorm,
    AdaptiveSystemeSenatProzedur,
    AdaptiveSystemeSenatTyp,
    AdaptiveSystemeSenat,
    build_adaptive_systeme_senat,
)
from .synergetik_norm import (
    SynergetikNormGeltung,
    SynergetikNormEintrag,
    SynergetikNormProzedur,
    SynergetikNormTyp,
    SynergetikNormSatz,
    build_synergetik_norm,
)
from .kuenstliches_leben_charta import (
    KuenstlichesLebenChartaGeltung,
    KuenstlichesLebenChartaNorm,
    KuenstlichesLebenChartaProzedur,
    KuenstlichesLebenChartaTyp,
    KuenstlichesLebenCharta,
    build_kuenstliches_leben_charta,
)
from .komplexe_systeme_verfassung import (
    KomplexeSystemeVerfassungsGeltung,
    KomplexeSystemeVerfassungsNorm,
    KomplexeSystemeVerfassungsProzedur,
    KomplexeSystemeVerfassungsTyp,
    KomplexeSystemeVerfassung,
    build_komplexe_systeme_verfassung,
)
from .informations_feld import (
    InformationsFeldGeltung, InformationsFeldNorm, InformationsFeldProzedur,
    InformationsFeldTyp, InformationsFeld, build_informations_feld,
)
from .kanal_register import (
    KanalRegisterGeltung, KanalRegisterNorm, KanalRegisterProzedur,
    KanalRegisterTyp, KanalRegister, build_kanal_register,
)
from .kybernetik_charta import (
    KybernetikChartaGeltung, KybernetikChartaNorm, KybernetikChartaProzedur,
    KybernetikChartaTyp, KybernetikCharta, build_kybernetik_charta,
)
from .regelkreis_kodex import (
    RegelkreisKodexGeltung, RegelkreisKodexNorm, RegelkreisKodexProzedur,
    RegelkreisKodexTyp, RegelkreisKodex, build_regelkreis_kodex,
)
from .entropie_pakt import (
    EntropiePaktGeltung, EntropiePaktNorm, EntropiePaktProzedur,
    EntropiePaktTyp, EntropiePakt, build_entropie_pakt,
)
from .selbstregulations_manifest import (
    SelbstregulationsManifestGeltung, SelbstregulationsManifestNorm, SelbstregulationsManifestProzedur,
    SelbstregulationsManifestTyp, SelbstregulationsManifest, build_selbstregulations_manifest,
)
from .rueckkopplungs_senat import (
    RueckkopplungsSenatGeltung, RueckkopplungsSenatNorm, RueckkopplungsSenatProzedur,
    RueckkopplungsSenatTyp, RueckkopplungsSenat, build_rueckkopplungs_senat,
)
from .kybernetik_norm import (
    KybernetikNormGeltung, KybernetikNormEintrag, KybernetikNormProzedur,
    KybernetikNormTyp, KybernetikNormSatz, build_kybernetik_norm,
)
from .komplexitaets_steuerungs_charta import (
    KomplexitaetsSteuerungsChartaGeltung, KomplexitaetsSteuerungsChartaNorm, KomplexitaetsSteuerungsChartaProzedur,
    KomplexitaetsSteuerungsChartaTyp, KomplexitaetsSteuerungsCharta, build_komplexitaets_steuerungs_charta,
)
from .informations_verfassung import (
    InformationsVerfassungsGeltung, InformationsVerfassungsNorm, InformationsVerfassungsProzedur,
    InformationsVerfassungsTyp, InformationsVerfassung, build_informations_verfassung,
)
from .neuronales_feld import (
    NeuronalesFeldGeltung, NeuronalesFeldNorm, NeuronalesFeldProzedur,
    NeuronalesFeldTyp, NeuronalesFeld, build_neuronales_feld,
)
from .synaptik_register import (
    SynaptikRegisterGeltung, SynaptikRegisterNorm, SynaptikRegisterProzedur,
    SynaptikRegisterTyp, SynaptikRegister, build_synaptik_register,
)
from .kortex_charta import (
    KortexChartaGeltung, KortexChartaNorm, KortexChartaProzedur,
    KortexChartaTyp, KortexCharta, build_kortex_charta,
)
from .gedaechtnis_kodex import (
    GedaechnisKodexGeltung, GedaechnisKodexNorm, GedaechnisKodexProzedur,
    GedaechnisKodexTyp, GedaechnisKodex, build_gedaechtnis_kodex,
)
from .bewusstseins_pakt import (
    BewusstseinsPaktGeltung, BewusstseinsPaktNorm, BewusstseinsPaktProzedur,
    BewusstseinsPaktTyp, BewusstseinsPakt, build_bewusstseins_pakt,
)
from .wahrnehmungs_manifest import (
    WahrnehmungsManifestGeltung, WahrnehmungsManifestNorm, WahrnehmungsManifestProzedur,
    WahrnehmungsManifestTyp, WahrnehmungsManifest, build_wahrnehmungs_manifest,
)
from .aufmerksamkeits_senat import (
    AufmerksamkeitsSenatGeltung, AufmerksamkeitsSenatNorm, AufmerksamkeitsSenatProzedur,
    AufmerksamkeitsSenatTyp, AufmerksamkeitsSenat, build_aufmerksamkeits_senat,
)
from .kognitions_norm import (
    KognitionsNormGeltung, KognitionsNormEintrag, KognitionsNormProzedur,
    KognitionsNormTyp, KognitionsNormSatz, build_kognitions_norm,
)
from .emotions_charta import (
    EmotionsChartaGeltung, EmotionsChartaNorm, EmotionsChartaProzedur,
    EmotionsChartaTyp, EmotionsCharta, build_emotions_charta,
)
from .neurowissenschafts_verfassung import (
    NeurowissenschaftsVerfassungsGeltung, NeurowissenschaftsVerfassungsNorm,
    NeurowissenschaftsVerfassungsProzedur, NeurowissenschaftsVerfassungsTyp,
    NeurowissenschaftsVerfassung, build_neurowissenschafts_verfassung,
)
from .spieltheorie_feld import (
    SpieltheorieFeldGeltung, SpieltheorieFeldNorm,
    SpieltheorieFeldProzedur, SpieltheorieFeldTyp,
    SpieltheorieFeld, build_spieltheorie_feld,
)
from .nash_register import (
    NashRegisterGeltung, NashRegisterNorm,
    NashRegisterProzedur, NashRegisterTyp,
    NashRegister, build_nash_register,
)
from .kooperations_charta import (
    KooperationsChartaGeltung, KooperationsChartaNorm,
    KooperationsChartaProzedur, KooperationsChartaTyp,
    KooperationsCharta, build_kooperations_charta,
)
from .mechanismus_kodex import (
    MechanismusKodexGeltung, MechanismusKodexNorm,
    MechanismusKodexProzedur, MechanismusKodexTyp,
    MechanismusKodex, build_mechanismus_kodex,
)
from .entscheidungs_pakt import (
    EntscheidungsPaktGeltung, EntscheidungsPaktNorm,
    EntscheidungsPaktProzedur, EntscheidungsPaktTyp,
    EntscheidungsPakt, build_entscheidungs_pakt,
)
from .rationalitaets_manifest import (
    RationalitaetsManifestGeltung, RationalitaetsManifestNorm,
    RationalitaetsManifestProzedur, RationalitaetsManifestTyp,
    RationalitaetsManifest, build_rationalitaets_manifest,
)
from .auktions_senat import (
    AuktionsSenatGeltung, AuktionsSenatNorm,
    AuktionsSenatProzedur, AuktionsSenatTyp,
    AuktionsSenat, build_auktions_senat,
)
from .spieltheorie_norm import (
    SpieltheorieNormGeltung, SpieltheorieNormEintrag,
    SpieltheorieNormProzedur, SpieltheorieNormTyp,
    SpieltheorieNormSatz, build_spieltheorie_norm,
)
from .gleichgewichts_charta import (
    GleichgewichtsChartaGeltung, GleichgewichtsChartaNorm,
    GleichgewichtsChartaProzedur, GleichgewichtsChartaTyp,
    GleichgewichtsCharta, build_gleichgewichts_charta,
)
from .entscheidungstheorie_verfassung import (
    EntscheidungstheorieVerfassungsGeltung, EntscheidungstheorieVerfassungsNorm,
    EntscheidungstheorieVerfassungsProzedur, EntscheidungstheorieVerfassungsTyp,
    EntscheidungstheorieVerfassung, build_entscheidungstheorie_verfassung,
)
from .evolutions_feld import (
    EvolutionsFeldGeltung, EvolutionsFeldNorm,
    EvolutionsFeldProzedur, EvolutionsFeldTyp,
    EvolutionsFeld, build_evolutions_feld,
)
from .genetik_register import (
    GenetikRegisterGeltung, GenetikRegisterNorm,
    GenetikRegisterProzedur, GenetikRegisterTyp,
    GenetikRegister, build_genetik_register,
)
from .selektions_charta import (
    SeletkionsChartaGeltung, SeletkionsChartaNorm,
    SeletkionsChartaProzedur, SeletkionsChartaTyp,
    SeletkionsCharta, build_selektions_charta,
)
from .mutations_kodex import (
    MutationsKodexGeltung, MutationsKodexNorm,
    MutationsKodexProzedur, MutationsKodexTyp,
    MutationsKodex, build_mutations_kodex,
)
from .fitness_pakt import (
    FitnessPaktGeltung, FitnessPaktNorm,
    FitnessPaktProzedur, FitnessPaktTyp,
    FitnessPakt, build_fitness_pakt,
)
from .adaptations_manifest import (
    AdaptationsManifestGeltung, AdaptationsManifestNorm,
    AdaptationsManifestProzedur, AdaptationsManifestTyp,
    AdaptationsManifest, build_adaptations_manifest,
)
from .oekologie_senat import (
    OekologieSenatGeltung, OekologieSenatNorm,
    OekologieSenatProzedur, OekologieSenatTyp,
    OekologieSenat, build_oekologie_senat,
)
from .evolutions_norm import (
    EvolutionsNormGeltung, EvolutionsNormEintrag,
    EvolutionsNormProzedur, EvolutionsNormTyp,
    EvolutionsNormSatz, build_evolutions_norm,
)
from .phylogenetik_charta import (
    PhylogenetikChartaGeltung, PhylogenetikChartaNorm,
    PhylogenetikChartaProzedur, PhylogenetikChartaTyp,
    PhylogenetikCharta, build_phylogenetik_charta,
)
from .evolutionsbiologie_verfassung import (
    EvolutionsbiologieVerfassungsGeltung, EvolutionsbiologieVerfassungsNorm,
    EvolutionsbiologieVerfassungsProzedur, EvolutionsbiologieVerfassungsTyp,
    EvolutionsbiologieVerfassung, build_evolutionsbiologie_verfassung,
)
from .sprach_feld import (
    SprachFeldGeltung, SprachFeldNorm,
    SprachFeldProzedur, SprachFeldTyp,
    SprachFeld, build_sprach_feld,
)
from .phonologie_register import (
    PhonologieRegisterGeltung, PhonologieRegisterNorm,
    PhonologieRegisterProzedur, PhonologieRegisterTyp,
    PhonologieRegister, build_phonologie_register,
)
from .syntax_charta import (
    SyntaxChartaGeltung, SyntaxChartaNorm,
    SyntaxChartaProzedur, SyntaxChartaTyp,
    SyntaxCharta, build_syntax_charta,
)
from .semantik_kodex import (
    SemantikKodexGeltung, SemantikKodexNorm,
    SemantikKodexProzedur, SemantikKodexTyp,
    SemantikKodex, build_semantik_kodex,
)
from .pragmatik_pakt import (
    PragmatikPaktGeltung, PragmatikPaktNorm,
    PragmatikPaktProzedur, PragmatikPaktTyp,
    PragmatikPakt, build_pragmatik_pakt,
)
from .semiotik_manifest import (
    SemiotikManifestGeltung, SemiotikManifestNorm,
    SemiotikManifestProzedur, SemiotikManifestTyp,
    SemiotikManifest, build_semiotik_manifest,
)
from .diskurs_senat import (
    DiskursSenatGeltung, DiskursSenatNorm,
    DiskursSenatProzedur, DiskursSenatTyp,
    DiskursSenat, build_diskurs_senat,
)
from .sprach_norm import (
    SprachNormGeltung, SprachNormEintrag,
    SprachNormProzedur, SprachNormTyp,
    SprachNormSatz, build_sprach_norm,
)
from .kommunikations_charta import (
    KommunikationsChartaGeltung, KommunikationsChartaNorm,
    KommunikationsChartaProzedur, KommunikationsChartaTyp,
    KommunikationsCharta, build_kommunikations_charta,
)
from .linguistik_verfassung import (
    LinguistikVerfassungsGeltung, LinguistikVerfassungsNorm,
    LinguistikVerfassungsProzedur, LinguistikVerfassungsTyp,
    LinguistikVerfassung, build_linguistik_verfassung,
)
from .erkenntnis_feld import (
    ErkenntnisFeldGeltung, ErkenntnisFeldNorm,
    ErkenntnisFeldProzedur, ErkenntnisFeldTyp,
    ErkenntnisFeld, build_erkenntnis_feld,
)
from .ontologie_register import (
    OntologieRegisterGeltung, OntologieRegisterNorm,
    OntologieRegisterProzedur, OntologieRegisterTyp,
    OntologieRegister, build_ontologie_register,
)
from .epistemologie_charta import (
    EpistemologieChartaGeltung, EpistemologieChartaNorm,
    EpistemologieChartaProzedur, EpistemologieChartaTyp,
    EpistemologieCharta, build_epistemologie_charta,
)
from .rationalismus_kodex import (
    RationalismusKodexGeltung, RationalismusKodexNorm,
    RationalismusKodexProzedur, RationalismusKodexTyp,
    RationalismusKodex, build_rationalismus_kodex,
)
from .wissenschafts_pakt import (
    WissenschaftsPaktGeltung, WissenschaftsPaktNorm,
    WissenschaftsPaktProzedur, WissenschaftsPaktTyp,
    WissenschaftsPakt, build_wissenschafts_pakt,
)
from .paradigmen_manifest import (
    ParadigmenManifestGeltung, ParadigmenManifestNorm,
    ParadigmenManifestProzedur, ParadigmenManifestTyp,
    ParadigmenManifest, build_paradigmen_manifest,
)
from .logik_senat import (
    LogikSenatGeltung, LogikSenatNorm,
    LogikSenatProzedur, LogikSenatTyp,
    LogikSenat, build_logik_senat,
)
from .erkenntnis_norm import (
    ErkenntnisNormGeltung, ErkenntnisNormEintrag,
    ErkenntnisNormProzedur, ErkenntnisNormTyp,
    ErkenntnisNormSatz, build_erkenntnis_norm,
)
from .meta_kognitions_charta import (
    MetaKognitionsChartaGeltung, MetaKognitionsChartaNorm,
    MetaKognitionsChartaProzedur, MetaKognitionsChartaTyp,
    MetaKognitionsCharta, build_meta_kognitions_charta,
)
from .philosophie_verfassung import (
    PhilosophieVerfassungsGeltung, PhilosophieVerfassungsNorm,
    PhilosophieVerfassungsProzedur, PhilosophieVerfassungsTyp,
    PhilosophieVerfassung, build_philosophie_verfassung,
)
from .kybernetik_feld import (
    KybernetikFeldGeltung, KybernetikFeldNorm,
    KybernetikFeldProzedur, KybernetikFeldTyp,
    KybernetikFeld, build_kybernetik_feld,
)
from .systemtheorie_register import (
    SystemtheorieRegisterGeltung, SystemtheorieRegisterNorm,
    SystemtheorieRegisterProzedur, SystemtheorieRegisterTyp,
    SystemtheorieRegister, build_systemtheorie_register,
)
from .autopoiesis_charta import (
    AutopoiesisChartaGeltung, AutopoiesisChartaNorm,
    AutopoiesisChartaProzedur, AutopoiesisChartaTyp,
    AutopoiesisCharta, build_autopoiesis_charta,
)
from .homoeostase_kodex import (
    HomoeostaseKodexGeltung, HomoeostaseKodexNorm,
    HomoeostaseKodexProzedur, HomoeostaseKodexTyp,
    HomoeostaseKodex, build_homoeostase_kodex,
)
from .rekursions_pakt import (
    RekursionsPaktGeltung, RekursionsPaktNorm,
    RekursionsPaktProzedur, RekursionsPaktTyp,
    RekursionsPakt, build_rekursions_pakt,
)
from .viable_system_manifest import (
    ViableSystemManifestGeltung, ViableSystemManifestNorm,
    ViableSystemManifestProzedur, ViableSystemManifestTyp,
    ViableSystemManifest, build_viable_system_manifest,
)
from .zweite_ordnung_senat import (
    ZweiteOrdnungSenatGeltung, ZweiteOrdnungSenatNorm,
    ZweiteOrdnungSenatProzedur, ZweiteOrdnungSenatTyp,
    ZweiteOrdnungSenat, build_zweite_ordnung_senat,
)
from .system_norm import (
    SystemNormGeltung, SystemNormEintrag,
    SystemNormProzedur, SystemNormTyp,
    SystemNormSatz, build_system_norm,
)
from .komplexitaets_adaptions_charta import (
    KomplexitaetsAdaptionsChartaGeltung, KomplexitaetsAdaptionsChartaNorm,
    KomplexitaetsAdaptionsChartaProzedur, KomplexitaetsAdaptionsChartaTyp,
    KomplexitaetsAdaptionsCharta, build_komplexitaets_adaptions_charta,
)
from .kybernetik_verfassung import (
    KybernetikVerfassungsGeltung, KybernetikVerfassungsNorm,
    KybernetikVerfassungsProzedur, KybernetikVerfassungsTyp,
    KybernetikVerfassung, build_kybernetik_verfassung,
)
from .soziologie_feld import (
    SoziologieFeldGeltung, SoziologieFeldNorm,
    SoziologieFeldProzedur, SoziologieFeldTyp,
    SoziologieFeld, build_soziologie_feld,
)
from .gesellschafts_register import (
    GesellschaftsRegisterGeltung, GesellschaftsRegisterNorm,
    GesellschaftsRegisterProzedur, GesellschaftsRegisterTyp,
    GesellschaftsRegister, build_gesellschafts_register,
)
from .klassen_charta import (
    KlassenChartaGeltung, KlassenChartaNorm,
    KlassenChartaProzedur, KlassenChartaTyp,
    KlassenCharta, build_klassen_charta,
)
from .struktur_kodex import (
    StrukturKodexGeltung, StrukturKodexNorm,
    StrukturKodexProzedur, StrukturKodexTyp,
    StrukturKodex, build_struktur_kodex,
)
from .habitus_manifest import (
    HabitusManifestGeltung, HabitusManifestNorm,
    HabitusManifestProzedur, HabitusManifestTyp,
    HabitusManifest, build_habitus_manifest,
)
from .strukturierungs_pakt import (
    StrukturierungsPaktGeltung, StrukturierungsPaktNorm,
    StrukturierungsPaktProzedur, StrukturierungsPaktTyp,
    StrukturierungsPakt, build_strukturierungs_pakt,
)
from .kommunikations_senat import (
    KommunikationsSenatGeltung, KommunikationsSenatNorm,
    KommunikationsSenatProzedur, KommunikationsSenatTyp,
    KommunikationsSenat, build_kommunikations_senat,
)
from .soziologie_norm import (
    SoziologieNormGeltung, SoziologieNormEintrag,
    SoziologieNormProzedur, SoziologieNormTyp,
    SoziologieNormSatz, build_soziologie_norm,
)
from .netzwerkgesellschafts_charta import (
    NetzwerkgesellschaftsChartaGeltung, NetzwerkgesellschaftsChartaNorm,
    NetzwerkgesellschaftsChartaProzedur, NetzwerkgesellschaftsChartaTyp,
    NetzwerkgesellschaftsCharta, build_netzwerkgesellschafts_charta,
)
from .soziologie_verfassung import (
    SoziologieVerfassungsGeltung, SoziologieVerfassungsNorm,
    SoziologieVerfassungsProzedur, SoziologieVerfassungsTyp,
    SoziologieVerfassung, build_soziologie_verfassung,
)
from .ethik_feld import (
    EthikFeldGeltung, EthikFeldNorm,
    EthikFeldProzedur, EthikFeldTyp,
    EthikFeld, build_ethik_feld,
)
from .utilitarismus_register import (
    UtilitarismusRegisterGeltung, UtilitarismusRegisterNorm,
    UtilitarismusRegisterProzedur, UtilitarismusRegisterTyp,
    UtilitarismusRegister, build_utilitarismus_register,
)
from .gerechtigkeits_charta import (
    GerechtigkeitsChartaGeltung, GerechtigkeitsChartaNorm,
    GerechtigkeitsChartaProzedur, GerechtigkeitsChartaTyp,
    GerechtigkeitsCharta, build_gerechtigkeits_charta,
)
from .tugend_kodex import (
    TugendKodexGeltung, TugendKodexNorm,
    TugendKodexProzedur, TugendKodexTyp,
    TugendKodex, build_tugend_kodex,
)
from .diskurs_manifest import (
    DiskursManifestGeltung, DiskursManifestNorm,
    DiskursManifestProzedur, DiskursManifestTyp,
    DiskursManifest, build_diskurs_manifest,
)
from .fuersorge_ethik_pakt import (
    FuersorgeEthikPaktGeltung, FuersorgeEthikPaktNorm,
    FuersorgeEthikPaktProzedur, FuersorgeEthikPaktTyp,
    FuersorgeEthikPakt, build_fuersorge_ethik_pakt,
)
from .meta_ethik_senat import (
    MetaEthikSenatGeltung, MetaEthikSenatNorm,
    MetaEthikSenatProzedur, MetaEthikSenatTyp,
    MetaEthikSenat, build_meta_ethik_senat,
)
from .ethik_norm import (
    EthikNormGeltung, EthikNormEintrag,
    EthikNormProzedur, EthikNormTyp,
    EthikNormSatz, build_ethik_norm,
)
from .angewandte_ethik_charta import (
    AngewandteEthikChartaGeltung, AngewandteEthikChartaNorm,
    AngewandteEthikChartaProzedur, AngewandteEthikChartaTyp,
    AngewandteEthikCharta, build_angewandte_ethik_charta,
)
from .ethik_verfassung import (
    EthikVerfassungsGeltung, EthikVerfassungsNorm,
    EthikVerfassungsProzedur, EthikVerfassungsTyp,
    EthikVerfassung, build_ethik_verfassung,
)
from .politik_feld import (
    PolitikFeldGeltung, PolitikFeldNorm,
    PolitikFeldProzedur, PolitikFeldTyp,
    PolitikFeld, build_politik_feld,
)
from .staatstheorie_register import (
    StaatstheorieRegisterGeltung, StaatstheorieRegisterNorm,
    StaatstheorieRegisterProzedur, StaatstheorieRegisterTyp,
    StaatstheorieRegister, build_staatstheorie_register,
)
from .demokratie_charta import (
    DemokratieChartaGeltung, DemokratieChartaNorm,
    DemokratieChartaProzedur, DemokratieChartaTyp,
    DemokratieCharta, build_demokratie_charta,
)
from .macht_kodex import (
    MachtKodexGeltung, MachtKodexNorm,
    MachtKodexProzedur, MachtKodexTyp,
    MachtKodex, build_macht_kodex,
)
from .gewaltenteilungs_manifest import (
    GewaltenteilungsManifestGeltung, GewaltenteilungsManifestNorm,
    GewaltenteilungsManifestProzedur, GewaltenteilungsManifestTyp,
    GewaltenteilungsManifest, build_gewaltenteilungs_manifest,
)
from .legitimitaets_pakt import (
    LegitimitaetsPaktGeltung, LegitimitaetsPaktNorm,
    LegitimitaetsPaktProzedur, LegitimitaetsPaktTyp,
    LegitimitaetsPakt, build_legitimitaets_pakt,
)
from .globalpolitik_senat import (
    GlobalpolitikSenatGeltung, GlobalpolitikSenatNorm,
    GlobalpolitikSenatProzedur, GlobalpolitikSenatTyp,
    GlobalpolitikSenat, build_globalpolitik_senat,
)
from .politik_norm import (
    PolitikNormGeltung, PolitikNormEintrag,
    PolitikNormProzedur, PolitikNormTyp,
    PolitikNormSatz, build_politik_norm,
)
from .zivilgesellschafts_charta import (
    ZivilgesellschaftsChartaGeltung, ZivilgesellschaftsChartaNorm,
    ZivilgesellschaftsChartaProzedur, ZivilgesellschaftsChartaTyp,
    ZivilgesellschaftsCharta, build_zivilgesellschafts_charta,
)
from .politik_verfassung import (
    PolitikVerfassungsGeltung, PolitikVerfassungsNorm,
    PolitikVerfassungsProzedur, PolitikVerfassungsTyp,
    PolitikVerfassung, build_politik_verfassung,
)
from .wirtschafts_feld import (
    WirtschaftsFeldGeltung, WirtschaftsFeldNorm,
    WirtschaftsFeldProzedur, WirtschaftsFeldTyp,
    WirtschaftsFeld, build_wirtschafts_feld,
)
from .markt_register import (
    MarktRegisterGeltung, MarktRegisterNorm,
    MarktRegisterProzedur, MarktRegisterTyp,
    MarktRegister, build_markt_register,
)
from .kapital_charta import (
    KapitalChartaGeltung, KapitalChartaNorm,
    KapitalChartaProzedur, KapitalChartaTyp,
    KapitalCharta, build_kapital_charta,
)
from .konjunktur_kodex import (
    KonjunkturKodexGeltung, KonjunkturKodexNorm,
    KonjunkturKodexProzedur, KonjunkturKodexTyp,
    KonjunkturKodex, build_konjunktur_kodex,
)
from .wirtschafts_ordnungs_manifest import (
    WirtschaftsOrdnungsManifestGeltung, WirtschaftsOrdnungsManifestNorm,
    WirtschaftsOrdnungsManifestProzedur, WirtschaftsOrdnungsManifestTyp,
    WirtschaftsOrdnungsManifest, build_ordnungs_manifest,
)
from .innovations_pakt import (
    InnovationsPaktGeltung, InnovationsPaktNorm,
    InnovationsPaktProzedur, InnovationsPaktTyp,
    InnovationsPakt, build_innovations_pakt,
)
from .wohlfahrts_senat import (
    WohlfahrtsSenatGeltung, WohlfahrtsSenatNorm,
    WohlfahrtsSenatProzedur, WohlfahrtsSenatTyp,
    WohlfahrtsSenat, build_wohlfahrts_senat,
)
from .wirtschafts_norm import (
    WirtschaftsNormGeltung, WirtschaftsNormEintrag,
    WirtschaftsNormProzedur, WirtschaftsNormTyp,
    WirtschaftsNormSatz, build_wirtschafts_norm,
)
from .institutionen_charta import (
    InstitutionenChartaGeltung, InstitutionenChartaNorm,
    InstitutionenChartaProzedur, InstitutionenChartaTyp,
    InstitutionenCharta, build_institutionen_charta,
)
from .wirtschafts_verfassung import (
    WirtschaftsVerfassungsGeltung, WirtschaftsVerfassungsNorm,
    WirtschaftsVerfassungsProzedur, WirtschaftsVerfassungsTyp,
    WirtschaftsVerfassung, build_wirtschafts_verfassung,
)
from .rechts_feld import (
    RechtsFeldGeltung, RechtsFeldNorm, RechtsFeldProzedur, RechtsFeldTyp,
    RechtsFeld, build_rechts_feld,
)
from .rechts_system_register import (
    RechtssystemRegisterGeltung, RechtssystemRegisterNorm,
    RechtssystemRegisterProzedur, RechtssystemRegisterTyp,
    RechtssystemRegister, build_rechts_system_register,
)
from .verfassungsrechts_charta import (
    VerfassungsrechtsChartaGeltung, VerfassungsrechtsChartaNorm,
    VerfassungsrechtsChartaProzedur, VerfassungsrechtsChartaTyp,
    VerfassungsrechtsCharta, build_verfassungsrechts_charta,
)
from .voelkerrechts_kodex import (
    VoelkerrechtsKodexGeltung, VoelkerrechtsKodexNorm,
    VoelkerrechtsKodexProzedur, VoelkerrechtsKodexTyp,
    VoelkerrechtsKodex as VoelkerrechtsKodexJurisprudenz,
    build_voelkerrechts_kodex as build_voelkerrechts_kodex_jurisprudenz,
)
from .rechtsphilosophie_manifest import (
    RechtsphilosophieManifestGeltung, RechtsphilosophieManifestNorm,
    RechtsphilosophieManifestProzedur, RechtsphilosophieManifestTyp,
    RechtsphilosophieManifest, build_rechtsphilosophie_manifest,
)
from .rechtssoziologie_pakt import (
    RechtssoziologiePaktGeltung, RechtssoziologiePaktNorm,
    RechtssoziologiePaktProzedur, RechtssoziologiePaktTyp,
    RechtssoziologiePakt, build_rechtssoziologie_pakt,
)
from .strafrechts_senat import (
    StrafrechtsSenatGeltung, StrafrechtsSenatNorm,
    StrafrechtsSenatProzedur, StrafrechtsSenatTyp,
    StrafrechtsSenat, build_strafrechts_senat,
)
from .rechts_norm import (
    RechtsNormGeltung, RechtsNormEintrag, RechtsNormProzedur, RechtsNormTyp,
    RechtsNormSatz, build_rechts_norm,
)
from .zivilrechts_charta import (
    ZivilrechtsChartaGeltung, ZivilrechtsChartaNorm,
    ZivilrechtsChartaProzedur, ZivilrechtsChartaTyp,
    ZivilrechtsCharta, build_zivilrechts_charta,
)
from .rechts_verfassung import (
    RechtsVerfassungsGeltung, RechtsVerfassungsNorm,
    RechtsVerfassungsProzedur, RechtsVerfassungsTyp,
    RechtsVerfassung, build_rechts_verfassung,
)
# --- Block #35: Geschichtswissenschaft & Historiographie (#541–#550) ---
from .geschichts_feld import (
    GeschichtsFeldGeltung, GeschichtsFeldNorm,
    GeschichtsFeldProzedur, GeschichtsFeldTyp,
    GeschichtsFeld, build_geschichts_feld,
)
from .historiographie_register import (
    HistoriographieRegisterGeltung, HistoriographieRegisterNorm,
    HistoriographieRegisterProzedur, HistoriographieRegisterTyp,
    HistoriographieRegister, build_historiographie_register,
)
from .quellen_charta import (
    QuellenChartaGeltung, QuellenChartaNorm,
    QuellenChartaProzedur, QuellenChartaTyp,
    QuellenCharta, build_quellen_charta,
)
from .epochen_kodex import (
    EpochenKodexGeltung, EpochenKodexNorm,
    EpochenKodexProzedur, EpochenKodexTyp,
    EpochenKodex, build_epochen_kodex,
)
from .annales_manifest import (
    AnnalesManifestGeltung, AnnalesManifestNorm,
    AnnalesManifestProzedur, AnnalesManifestTyp,
    AnnalesManifest, build_annales_manifest,
)
from .zeitgeschichts_pakt import (
    ZeitgeschichtsPaktGeltung, ZeitgeschichtsPaktNorm,
    ZeitgeschichtsPaktProzedur, ZeitgeschichtsPaktTyp,
    ZeitgeschichtsPakt, build_zeitgeschichts_pakt,
)
from .geschichts_senat import (
    GeschichtsSenatGeltung, GeschichtsSenatNorm,
    GeschichtsSenatProzedur, GeschichtsSenatTyp,
    GeschichtsSenat, build_geschichts_senat,
)
from .geschichts_norm import (
    GeschichtsNormGeltung, GeschichtsNormEintrag,
    GeschichtsNormProzedur, GeschichtsNormTyp,
    GeschichtsNormSatz, build_geschichts_norm,
)
from .historiographie_charta import (
    HistoriographieChartaGeltung, HistoriographieChartaNorm,
    HistoriographieChartaProzedur, HistoriographieChartaTyp,
    HistoriographieCharta, build_historiographie_charta,
)
from .geschichts_verfassung import (
    GeschichtsVerfassungsGeltung, GeschichtsVerfassungsNorm,
    GeschichtsVerfassungsProzedur, GeschichtsVerfassungsTyp,
    GeschichtsVerfassung, build_geschichts_verfassung,
)
from .kultur_feld import (
    KulturFeldGeltung, KulturFeldNorm, KulturFeldProzedur, KulturFeldTyp,
    KulturFeld, build_kultur_feld,
)
from .kulturanthropologie_register import (
    KulturanthropologieRegisterGeltung, KulturanthropologieRegisterNorm,
    KulturanthropologieRegisterProzedur, KulturanthropologieRegisterTyp,
    KulturanthropologieRegister, build_kulturanthropologie_register,
)
from .ethnographie_charta import (
    EthnographieChartaGeltung, EthnographieChartaNorm,
    EthnographieChartaProzedur, EthnographieChartaTyp,
    EthnographieCharta, build_ethnographie_charta,
)
from .ritual_kodex import (
    RitualKodexGeltung, RitualKodexNorm, RitualKodexProzedur, RitualKodexTyp,
    RitualKodex, build_ritual_kodex,
)
from .kultursysteme_manifest import (
    KultursystemeManifestGeltung, KultursystemeManifestNorm,
    KultursystemeManifestProzedur, KultursystemeManifestTyp,
    KultursystemeManifest, build_kultursysteme_manifest,
)
from .kulturgedaechtnis_pakt import (
    KulturgedaechnisPaktGeltung, KulturgedaechnisPaktNorm,
    KulturgedaechnisPaktProzedur, KulturgedaechnisPaktTyp,
    KulturgedaechnisPakt, build_kulturgedaechtnis_pakt,
)
from .kultursoziologie_senat import (
    KultursoziologieSenatGeltung, KultursoziologieSenatNorm,
    KultursoziologieSenatProzedur, KultursoziologieSenatTyp,
    KultursoziologieSenat, build_kultursoziologie_senat,
)
from .kultur_norm import (
    KulturNormTyp, KulturNormProzedur, KulturNormGeltung,
    KulturNormEintrag, KulturNormSatz, build_kultur_norm,
)
from .kulturelle_identitaets_charta import (
    KulturelleIdentitaetsChartaGeltung, KulturelleIdentitaetsChartaNorm,
    KulturelleIdentitaetsChartaProzedur, KulturelleIdentitaetsChartaTyp,
    KulturelleIdentitaetsCharta, build_kulturelle_identitaets_charta,
)
from .kultur_verfassung import (
    KulturVerfassungsGeltung, KulturVerfassungsNorm,
    KulturVerfassungsProzedur, KulturVerfassungsTyp,
    KulturVerfassung, build_kultur_verfassung,
)
from .medien_feld import (
    MedienFeldGeltung, MedienFeldNorm, MedienFeldProzedur, MedienFeldTyp,
    MedienFeld, build_medien_feld,
)
from .kommunikations_register import (
    KommunikationsRegisterGeltung, KommunikationsRegisterNorm,
    KommunikationsRegisterProzedur, KommunikationsRegisterTyp,
    KommunikationsRegister, build_kommunikations_register,
)
from .medientheorie_charta import (
    MedientheorieChartaGeltung, MedientheorieChartaNorm,
    MedientheorieChartaProzedur, MedientheorieChartaTyp,
    MedientheorieCharta, build_medientheorie_charta,
)
from .informations_kodex import (
    InformationsKodexGeltung, InformationsKodexNorm,
    InformationsKodexProzedur, InformationsKodexTyp,
    InformationsKodex, build_informations_kodex,
)
from .medien_diskurs_manifest import (
    DiskursManifestGeltung as MedienDiskursManifestGeltung,
    DiskursManifestNorm as MedienDiskursManifestNorm,
    DiskursManifestProzedur as MedienDiskursManifestProzedur,
    DiskursManifestTyp as MedienDiskursManifestTyp,
    DiskursManifest as MedienDiskursManifest,
    build_diskurs_manifest as build_medien_diskurs_manifest,
)
from .oeffentlichkeits_pakt import (
    OeffentlichkeitsPaktGeltung, OeffentlichkeitsPaktNorm,
    OeffentlichkeitsPaktProzedur, OeffentlichkeitsPaktTyp,
    OeffentlichkeitsPakt, build_oeffentlichkeits_pakt,
)
from .medien_senat import (
    MedienSenatGeltung, MedienSenatNorm, MedienSenatProzedur, MedienSenatTyp,
    MedienSenat, build_medien_senat,
)
from .medien_norm import (
    MedienNormTyp, MedienNormProzedur, MedienNormGeltung,
    MedienNormEintrag, MedienNormSatz, build_medien_norm,
)
from .kommunikative_handlungs_charta import (
    KommunikativeHandlungsChartaGeltung, KommunikativeHandlungsChartaNorm,
    KommunikativeHandlungsChartaProzedur, KommunikativeHandlungsChartaTyp,
    KommunikativeHandlungsCharta, build_kommunikative_handlungs_charta,
)
from .medien_verfassung import (
    MedienVerfassungsGeltung, MedienVerfassungsNorm,
    MedienVerfassungsProzedur, MedienVerfassungsTyp,
    MedienVerfassung, build_medien_verfassung,
)
from .kunst_feld import (
    KunstFeldGeltung, KunstFeldNorm, KunstFeldProzedur, KunstFeldTyp,
    KunstFeld, build_kunst_feld,
)
from .aesthetik_register import (
    AesthetikRegisterGeltung, AesthetikRegisterNorm, AesthetikRegisterProzedur, AesthetikRegisterTyp,
    AesthetikRegister, build_aesthetik_register,
)
from .kunsttheorie_charta import (
    KunsttheorieChartaGeltung, KunsttheorieChartaNorm, KunsttheorieChartaProzedur, KunsttheorieChartaTyp,
    KunsttheorieCharta, build_kunsttheorie_charta,
)
from .stilkritik_kodex import (
    StilkritikKodexGeltung, StilkritikKodexNorm, StilkritikKodexProzedur, StilkritikKodexTyp,
    StilkritikKodex, build_stilkritik_kodex,
)
from .kunstgeschichte_manifest import (
    KunstgeschichteManifestGeltung, KunstgeschichteManifestNorm, KunstgeschichteManifestProzedur, KunstgeschichteManifestTyp,
    KunstgeschichteManifest, build_kunstgeschichte_manifest,
)
from .ikonographie_pakt import (
    IkonographiePaktGeltung, IkonographiePaktNorm, IkonographiePaktProzedur, IkonographiePaktTyp,
    IkonographiePakt, build_ikonographie_pakt,
)
from .kunstsoziologie_senat import (
    KunstsoziologieSenatGeltung, KunstsoziologieSenatNorm, KunstsoziologieSenatProzedur, KunstsoziologieSenatTyp,
    KunstsoziologieSenat, build_kunstsoziologie_senat,
)
from .kunst_norm import (
    KunstNormTyp, KunstNormProzedur, KunstNormGeltung, KunstNormEintrag, KunstNormSatz, build_kunst_norm,
)
from .aesthetische_urteils_charta import (
    AesthetischeUrteilsChartaGeltung, AesthetischeUrteilsChartaNorm,
    AesthetischeUrteilsChartaProzedur, AesthetischeUrteilsChartaTyp,
    AesthetischeUrteilsCharta, build_aesthetische_urteils_charta,
)
from .kunst_verfassung import (
    KunstVerfassungsGeltung, KunstVerfassungsNorm, KunstVerfassungsProzedur, KunstVerfassungsTyp,
    KunstVerfassung, build_kunst_verfassung,
)
from .paedagogik_feld import (
    PaedagogikFeldGeltung, PaedagogikFeldNorm, PaedagogikFeldProzedur, PaedagogikFeldTyp,
    PaedagogikFeld, build_paedagogik_feld,
)
from .bildungstheorie_register import (
    BildungstheorieRegisterGeltung, BildungstheorieRegisterNorm, BildungstheorieRegisterProzedur, BildungstheorieRegisterTyp,
    BildungstheorieRegister, build_bildungstheorie_register,
)
from .lerntheorie_charta import (
    LerntheorieChartaGeltung, LerntheorieChartaNorm, LerntheorieChartaProzedur, LerntheorieChartaTyp,
    LerntheorieCharta, build_lerntheorie_charta,
)
from .didaktik_kodex import (
    DidaktikKodexGeltung, DidaktikKodexNorm, DidaktikKodexProzedur, DidaktikKodexTyp,
    DidaktikKodex, build_didaktik_kodex,
)
from .curriculum_manifest import (
    CurriculumManifestGeltung, CurriculumManifestNorm, CurriculumManifestProzedur, CurriculumManifestTyp,
    CurriculumManifest, build_curriculum_manifest,
)
from .bildungsinstitution_pakt import (
    BildungsinstitutionPaktGeltung, BildungsinstitutionPaktNorm, BildungsinstitutionPaktProzedur, BildungsinstitutionPaktTyp,
    BildungsinstitutionPakt, build_bildungsinstitution_pakt,
)
from .paedagogik_senat import (
    PaedagogikSenatGeltung, PaedagogikSenatNorm, PaedagogikSenatProzedur, PaedagogikSenatTyp,
    PaedagogikSenat, build_paedagogik_senat,
)
from .paedagogik_norm import (
    PaedagogikNormTyp, PaedagogikNormProzedur, PaedagogikNormGeltung, PaedagogikNormEintrag, PaedagogikNormSatz, build_paedagogik_norm,
)
from .bildungsphilosophie_charta import (
    BildungsphilosophieChartaGeltung, BildungsphilosophieChartaNorm,
    BildungsphilosophieChartaProzedur, BildungsphilosophieChartaTyp,
    BildungsphilosophieCharta, build_bildungsphilosophie_charta,
)
from .paedagogik_verfassung import (
    PaedagogikVerfassungsGeltung, PaedagogikVerfassungsNorm, PaedagogikVerfassungsProzedur, PaedagogikVerfassungsTyp,
    PaedagogikVerfassung, build_paedagogik_verfassung,
)
from .psychologie_feld import (
    PsychologieFeldGeltung, PsychologieFeldNorm, PsychologieFeldProzedur, PsychologieFeldTyp,
    PsychologieFeld, build_psychologie_feld,
)
from .kognitionswissenschaft_register import (
    KognitionswissenschaftRegisterGeltung, KognitionswissenschaftRegisterNorm, KognitionswissenschaftRegisterProzedur, KognitionswissenschaftRegisterTyp,
    KognitionswissenschaftRegister, build_kognitionswissenschaft_register,
)
from .bewusstseins_charta import (
    BewusstseinsChartaGeltung, BewusstseinsChartaNorm, BewusstseinsChartaProzedur, BewusstseinsChartaTyp,
    BewusstseinsCharta, build_bewusstseins_charta,
)
from .verhaltens_kodex import (
    VerhaltensKodexGeltung, VerhaltensKodexNorm, VerhaltensKodexProzedur, VerhaltensKodexTyp,
    VerhaltensKodex, build_verhaltens_kodex,
)
from .entwicklungs_manifest import (
    EntwicklungsManifestGeltung, EntwicklungsManifestNorm, EntwicklungsManifestProzedur, EntwicklungsManifestTyp,
    EntwicklungsManifest, build_entwicklungs_manifest,
)
from .sozialpsychologie_pakt import (
    SozialpsychologiePaktGeltung, SozialpsychologiePaktNorm, SozialpsychologiePaktProzedur, SozialpsychologiePaktTyp,
    SozialpsychologiePakt, build_sozialpsychologie_pakt,
)
from .psychologie_senat import (
    PsychologieSenatGeltung, PsychologieSenatNorm, PsychologieSenatProzedur, PsychologieSenatTyp,
    PsychologieSenat, build_psychologie_senat,
)
from .psychologie_norm import (
    PsychologieNormTyp, PsychologieNormProzedur, PsychologieNormGeltung, PsychologieNormEintrag, PsychologieNormSatz, build_psychologie_norm,
)
from .kognitions_charta import (
    KognitionsChartaGeltung, KognitionsChartaNorm, KognitionsChartaProzedur, KognitionsChartaTyp,
    KognitionsCharta, build_kognitions_charta,
)
from .psychologie_verfassung import (
    PsychologieVerfassungsGeltung, PsychologieVerfassungsNorm, PsychologieVerfassungsProzedur, PsychologieVerfassungsTyp,
    PsychologieVerfassung, build_psychologie_verfassung,
)
from .linguistik_feld import (
    LinguistikFeldGeltung, LinguistikFeldNorm, LinguistikFeldProzedur, LinguistikFeldTyp,
    LinguistikFeld, build_linguistik_feld,
)
from .sprachphonik_register import (
    PhonologieRegisterGeltung as SprachphonikRegisterGeltung,
    PhonologieRegisterNorm as SprachphonikRegisterNorm,
    PhonologieRegisterTyp as SprachphonikRegisterTyp,
    PhonologieRegister as SprachphonikRegister,
    build_phonologie_register as build_sprachphonik_register,
)
from .morphologie_charta import (
    MorphologieChartaGeltung, MorphologieChartaNorm, MorphologieChartaProzedur, MorphologieChartaTyp,
    MorphologieCharta, build_morphologie_charta,
)
from .syntax_kodex import (
    SyntaxKodexGeltung, SyntaxKodexNorm, SyntaxKodexProzedur, SyntaxKodexTyp,
    SyntaxKodex, build_syntax_kodex,
)
from .semantik_manifest import (
    SemantikManifestGeltung, SemantikManifestNorm, SemantikManifestProzedur, SemantikManifestTyp,
    SemantikManifest, build_semantik_manifest,
)
from .diskurs_pakt import (
    PragmatikPaktGeltung as DiskursPaktGeltung,
    PragmatikPaktNorm as DiskursPaktNorm,
    PragmatikPaktTyp as DiskursPaktTyp,
    PragmatikPakt as DiskursPakt,
    build_pragmatik_pakt as build_diskurs_pakt,
)
from .linguistik_senat import (
    LinguistikSenatGeltung, LinguistikSenatNorm, LinguistikSenatProzedur, LinguistikSenatTyp,
    LinguistikSenat, build_linguistik_senat,
)
from .linguistik_norm import (
    LinguistikNormTyp, LinguistikNormProzedur, LinguistikNormGeltung, LinguistikNormEintrag, LinguistikNormSatz, build_linguistik_norm,
)
from .semiotik_charta import (
    SemiotikChartaGeltung, SemiotikChartaNorm, SemiotikChartaProzedur, SemiotikChartaTyp,
    SemiotikCharta, build_semiotik_charta,
)
from .sprachwissenschaft_verfassung import (
    SprachwissenschaftVerfassungGeltung, SprachwissenschaftVerfassungsNorm, SprachwissenschaftVerfassungProzedur, SprachwissenschaftVerfassungTyp,
    SprachwissenschaftVerfassung, build_sprachwissenschaft_verfassung,
)
from .religions_feld import (
    ReligionsFeldGeltung, ReligionsFeldNorm, ReligionsFeldProzedur, ReligionsFeldTyp,
    ReligionsFeld, build_religions_feld,
)
from .mythos_register import (
    MythosRegisterGeltung, MythosRegisterNorm, MythosRegisterTyp,
    MythosRegister, build_mythos_register,
)
from .heilige_tradition_charta import (
    HeiligeTraditionChartaGeltung, HeiligeTraditionChartaNorm, HeiligeTraditionChartaTyp,
    HeiligeTraditionCharta, build_heilige_tradition_charta,
)
from .theologie_kodex import (
    TheologieKodexGeltung, TheologieKodexNorm, TheologieKodexTyp,
    TheologieKodex, build_theologie_kodex,
)
from .glaubens_manifest import (
    GlaubensManifestGeltung, GlaubensManifestNorm, GlaubensManifestTyp,
    GlaubensManifest, build_glaubens_manifest,
)
from .spiritualitaets_pakt import (
    SpiritualitaetsPaktGeltung, SpiritualitaetsPaktNorm, SpiritualitaetsPaktTyp,
    SpiritualitaetsPakt, build_spiritualitaets_pakt,
)
from .religionsphilosophie_senat import (
    ReligionsphilosophieSenatGeltung, ReligionsphilosophieSenatNorm, ReligionsphilosophieSenatTyp,
    ReligionsphilosophieSenat, build_religionsphilosophie_senat,
)
from .religions_norm import (
    ReligionsNormTyp, ReligionsNormProzedur, ReligionsNormGeltung, ReligionsNormEintrag, ReligionsNormSatz, build_religions_norm,
)
from .sakrale_charta import (
    SakraleChartaGeltung, SakraleChartaNorm, SakraleChartaProzedur, SakraleChartaTyp,
    SakraleCharta, build_sakrale_charta,
)
from .religionswissenschaft_verfassung import (
    ReligionswissenschaftVerfassungGeltung, ReligionswissenschaftVerfassungsNorm, ReligionswissenschaftVerfassungProzedur, ReligionswissenschaftVerfassungTyp,
    ReligionswissenschaftVerfassung, build_religionswissenschaft_verfassung,
)
from .federation_coordination import (
    FederationAlignmentStatus,
    FederationCell,
    FederationCoordination,
    FederationDomain,
    FederationHandoff,
    FederationHandoffPriority,
    build_federation_coordination,
)
from .learning_register import LearningPatternType, LearningRecord, LearningRegister, build_learning_register
from .operations_steward import OperationsSteward, OperationsStewardStatus, StewardDirective, StewardDirectiveType, build_operations_steward
from .outcome_ledger import OutcomeLedger, OutcomeRecord, OutcomeStatus, build_outcome_ledger
from .operating_constitution import (
    ConstitutionArticle,
    ConstitutionPrinciple,
    ConstitutionalAuthority,
    OperatingConstitution,
    build_operating_constitution,
)
from .playbook_catalog import PlaybookCatalog, PlaybookEntry, PlaybookReadiness, PlaybookType, build_playbook_catalog
from .policy_tuner import PolicyTuneAction, PolicyTuneEntry, PolicyTuner, build_policy_tuner
from .program_controller import (
    ProgramController,
    ProgramControllerStatus,
    ProgramDirective,
    ProgramTrack,
    ProgramTrackType,
    build_program_controller,
)
from .steward_workboard import StewardWorkboard, WorkboardItem, WorkboardLane, WorkboardQueue, WorkboardStatus, build_steward_workboard
from .readiness_cadence import (
    ReadinessCadence,
    ReadinessCadenceEntry,
    ReadinessCadenceStatus,
    ReadinessCadenceTrigger,
    ReadinessCadenceWindow,
    build_readiness_cadence,
)
from .recovery_drills import RecoveryDrill, RecoveryDrillStatus, RecoveryDrillSuite, build_recovery_drill_suite
from .drift_monitor import DriftMonitor, DriftObservation, DriftSeverity, build_drift_monitor
from .escalation_router import EscalationRoute, EscalationRoutePath, EscalationRouter, build_escalation_router
from .evidence_ledger import EvidenceLedger, EvidenceLedgerEntry, EvidenceLedgerSource, build_evidence_ledger
from .governance_agenda import GovernanceAgenda, GovernanceAgendaItem, GovernanceAgendaStatus, build_governance_agenda
from .governance import (
    GateDecision,
    GateOutcome,
    HumanDecision,
    HumanLoopGovernance,
    evaluate_gate,
    govern_recovery_orchestration,
)
from .improvement_orchestrator import (
    ImprovementExecutionMode,
    ImprovementOrchestrator,
    ImprovementPriority,
    ImprovementWave,
    build_improvement_orchestrator,
)
from .intervention_simulator import (
    InterventionFallback,
    InterventionMode,
    InterventionSimulation,
    InterventionSimulationStatus,
    InterventionSimulator,
    build_intervention_simulator,
)
from .guardrail_portfolio import (
    Guardrail,
    GuardrailDomain,
    GuardrailPolicyMode,
    GuardrailPortfolio,
    build_guardrail_portfolio,
)
from .escalation_coordinator import EscalationDirective, EscalationPath, EscalationPlan, coordinate_escalations
from .incident_detector import IncidentCause, IncidentReport, IncidentSeverity, OperationsIncident, detect_incidents
from .integrated_smoke import IntegratedSmokeBuild, run_integrated_smoke_build
from .mission_profiles import MissionPolicy, MissionProfile, MissionScenario, mission_profile_catalog, mission_profile_for_name
from .operations_run import IntegratedOperationsRun, run_integrated_operations
from .operations_cockpit import CockpitEntry, CockpitStatus, OperationsCockpit, build_operations_cockpit
from .portfolio_optimizer import PortfolioAction, PortfolioOptimizer, PortfolioPriority, PortfolioRecommendation, build_portfolio_optimizer
from .release_campaigns import (
    ReleaseCampaign,
    ReleaseCampaignStage,
    ReleaseCampaignStageType,
    ReleaseCampaignStatus,
    build_release_campaign,
)
from .remediation_campaigns import (
    RemediationCampaign,
    RemediationCampaignStage,
    RemediationCampaignStageType,
    RemediationCampaignStatus,
    build_remediation_campaign,
)
from .review_action_plan import (
    ReviewActionItem,
    ReviewActionPlan,
    ReviewActionPriority,
    ReviewActionType,
    build_review_action_plan,
)
from .risk_register import (
    RiskImpact,
    RiskLikelihood,
    RiskMitigationStatus,
    RiskRecord,
    RiskRegister,
    build_risk_register,
)
from .scenario_replay import ReplayMode, ScenarioReplayItem, ScenarioReplayResult, ScenarioReplaySuite, build_scenario_replay
from .readiness_review import ReadinessFinding, ReadinessFindingSeverity, ReadinessReview, build_readiness_review
from .runtime_scorecard import RuntimeScorecard, RuntimeScorecardEntry, build_runtime_scorecard
from .run_ledger import OperationsRunLedger, RunLedgerEntry, ledger_for_wave
from .message_protocols import (
    DeliveryGuarantee,
    DeliveryMode,
    EventEnvelope,
    MessageEnvelope,
    MessageKind,
    ProtocolContext,
    command_message,
    event_message,
    evidence_message,
    protocol_context,
    transfer_message,
)
from .module_boundaries import (
    ModuleBoundary,
    ModuleBoundaryName,
    module_boundaries,
    module_boundary,
    module_dependency_graph,
)
from .orchestration import (
    ClaimStatus,
    DispatchAssignment,
    DispatchLane,
    DispatchPlan,
    DispatchTriageMode,
    GateReadiness,
    GateState,
    HandoffMode,
    OperationalPressure,
    OrchestrationState,
    OrchestrationStatus,
    PressureLevel,
    WorkClaim,
    WorkCostProfile,
    WorkHandoff,
    WorkPriority,
    WorkStatus,
    WorkUnit,
    advance_orchestration_state,
    advance_work_unit,
    build_dispatch_plan,
    claim_for_work_unit,
    dispatch_priority_score,
    handoff_for_work_unit,
    orchestration_state_for_runtime,
    work_unit_for_state,
)
from .runtime_dna import (
    RuntimeDNA,
    RuntimeHooks,
    RuntimeIdentity,
    RuntimeStage,
    RuntimeThresholds,
    runtime_dna_for_profile,
    runtime_dna_from_env,
)
from .recovery import (
    RecoveryCheckpoint,
    RecoveryDisposition,
    RecoveryMode,
    RecoveryOrchestration,
    RecoveryOutcome,
    RollbackDirective,
    orchestrate_recovery_for_rollout,
    recovery_checkpoint_for_state,
    recovery_outcome,
    rollback_directive_for_checkpoint,
)
from .rollout import (
    RolloutPhase,
    RolloutState,
    advance_rollout_state,
    rollout_state_for_shadow,
)
from .security import (
    ActionName,
    ArtifactKind,
    ArtifactScope,
    AuthorizationDecision,
    AuthorizationIdentity,
    ControlArtifact,
    DelegationGrant,
    IdentityKind,
    LoadedControlPlane,
    OperatingMode,
    PermissionRule,
    RoleName,
    TrustLevel,
    ValidationStep,
    authorize_action,
    authorize_artifact,
    load_control_plane,
    permission_catalog,
    role_permissions,
)
from .shadow import (
    DryRunEvaluation,
    PreviewMode,
    ShadowCoordination,
    ShadowCoordinationMode,
    ShadowPreview,
    coordinate_shadow_work,
    evaluate_dry_run,
    shadow_event,
    shadow_preview_for_command,
    shadow_snapshot,
)
from .telemetry import (
    AuditTrailEntry,
    CorrelatedOperation,
    TelemetryAlert,
    TelemetrySignal,
    TelemetrySnapshot,
    audit_entry_for_artifact,
    audit_entry_for_message,
    build_telemetry_snapshot,
    correlate_operation,
    dispatch_signal,
    gate_signal,
    operation_alerts,
    telemetry_alert,
    telemetry_signal_from_event,
)
from .wave_orchestration import OperationsWave, WaveBudgetPolicy, WaveMissionExecution, run_operations_wave

__all__ = [
    "CoreState",
    "DeliveryGuarantee",
    "DeliveryMode",
    "DriftMonitor",
    "DriftObservation",
    "DriftSeverity",
    "EvidenceRecord",
    "EventEnvelope",
    "MessageEnvelope",
    "MessageKind",
    "ActionName",
    "ArtifactKind",
    "ArtifactScope",
    "AutonomyAssignment",
    "AutonomyDecision",
    "AutonomyGovernor",
    "AuthorizationDecision",
    "AuthorizationIdentity",
    "AuditTrailEntry",
    "BenchmarkCase",
    "BenchmarkCaseResult",
    "BenchmarkHarness",
    "BenchmarkReleaseMode",
    "CapacityLane",
    "CapacityPlanEntry",
    "CapacityPlanner",
    "CapacityWindow",
    "ContinuousReadinessCycle",
    "ContinuousReadinessIteration",
    "ContinuousReadinessStatus",
    "ConvergenceProjection",
    "ConvergenceSimulator",
    "ConvergenceStatus",
    "ChangeWindow",
    "ChangeWindowEntry",
    "ChangeWindowStatus",
    "CorrelatedOperation",
    "CockpitEntry",
    "CockpitStatus",
    "ControlArtifact",
    "DelegationGrant",
    "DryRunEvaluation",
    "ClaimStatus",
    "DispatchAssignment",
    "DispatchLane",
    "DispatchPlan",
    "DispatchTriageMode",
    "EscalationDirective",
    "EscalationPath",
    "EscalationPlan",
    "EscalationRoute",
    "EscalationRoutePath",
    "EscalationRouter",
    "EvidenceLedger",
    "EvidenceLedgerEntry",
    "EvidenceLedgerSource",
    "ExecutiveOrder",
    "ExecutiveOrderMode",
    "ExecutiveWatchStatus",
    "ExecutiveWatchtower",
    "StrategyCouncil",
    "StrategyCouncilStatus",
    "StrategyEscalationMandate",
    "StrategyLane",
    "StrategyMandate",
    "StrategyPriority",
    "MandateCard",
    "MandateCardDeck",
    "MandateExecutionScope",
    "MandateReviewCadence",
    "PortfolioConcentration",
    "PortfolioExposure",
    "PortfolioOperatingSpread",
    "PortfolioRadar",
    "PortfolioRadarEntry",
    "ScenarioChancery",
    "ScenarioOfficeMode",
    "ScenarioOfficeStatus",
    "ScenarioOption",
    "CourseCorrector",
    "CourseCorrectionAction",
    "CourseCorrectionDirective",
    "CourseCorrectionStatus",
    "MandateMemoryRecord",
    "MandateMemoryStatus",
    "MandateMemoryStore",
    "CompassStatus",
    "GuidelineCompass",
    "GuidelinePrinciple",
    "GuidelineVector",
    "NavigationConstraint",
    "CharterStatus",
    "InterventionCharter",
    "InterventionClause",
    "InterventionRight",
    "ReleaseThreshold",
    "StopCondition",
    "ProgramSenate",
    "SenateBalanceStatus",
    "SenatePriority",
    "SenateResolution",
    "SenateSeat",
    "ConsensusDirective",
    "ConsensusDirectiveStatus",
    "ConsensusDirectiveType",
    "ConsensusMandate",
    "DirectiveConsensus",
    "ArchiveEntry",
    "ArchiveRetention",
    "ArchiveStatus",
    "DecisionArchive",
    "CabinetExecutionMode",
    "CabinetOrder",
    "CabinetRole",
    "CabinetStatus",
    "ExecutionCabinet",
    "DelegationEntry",
    "DelegationLane",
    "DelegationMatrix",
    "DelegationMode",
    "DelegationStatus",
    "RecallPath",
    "ReleasePath",
    "SluiceStatus",
    "VetoChannel",
    "VetoSluice",
    "VetoStop",
    "ConsensusDiplomacy",
    "DiplomacyChannel",
    "DiplomacyPath",
    "DiplomacyPosture",
    "DiplomacyStatus",
    "DoctrineClause",
    "DoctrinePrinciple",
    "DoctrineScope",
    "DoctrineStatus",
    "LeitsternDoctrine",
    "CollegiumLane",
    "CollegiumMandate",
    "CollegiumSeat",
    "CollegiumStatus",
    "MissionsCollegium",
    "ConclaveLane",
    "ConclaveMotion",
    "ConclavePriority",
    "ConclaveStatus",
    "PriorityConclave",
    "ContractClause",
    "ContractCommitment",
    "ContractParty",
    "ContractStatus",
    "CourseContract",
    "CodexAxis",
    "CodexCanon",
    "CodexSection",
    "CodexStatus",
    "LeitsternCodex",
    "KodexRegister",
    "KodexRegisterEntry",
    "RegisterRetention",
    "RegisterTier",
    "RatBench",
    "RatInterpretation",
    "RatStatus",
    "SatzungsRat",
    "SatzungsRatArticle",
    "KonventEbene",
    "KonventMandat",
    "KonventStatus",
    "MandatsKonvent",
    "MandatsLinie",
    "NormenTribunal",
    "TribunalFall",
    "TribunalKammer",
    "TribunalUrteil",
    "TribunalVerfahren",
    "SenatsBeschluss",
    "SenatsFraktion",
    "SenatsSitzung",
    "SenatsMandat",
    "VerfassungsSenat",
    "ChartaArtikel",
    "ChartaGeltung",
    "ChartaKapitel",
    "ChartaVerfahren",
    "GrundrechtsCharta",
    "AktKlausel",
    "AktProzedur",
    "AktSektion",
    "AktStatus",
    "SouveraenitaetsAkt",
    "ManifestAbschnitt",
    "ManifestGeltung",
    "ManifestKapitel",
    "ManifestVerfahren",
    "OrdnungsManifest",
    "Leitordnung",
    "OrdnungsKraft",
    "OrdnungsNorm",
    "OrdnungsRang",
    "OrdnungsTyp",
    "AutoritaetsDekret",
    "DekretGeltung",
    "DekretKlausel",
    "DekretProzedur",
    "DekretSektion",
    "FundamentKraft",
    "FundamentPfeiler",
    "FundamentSaeule",
    "FundamentVerfahren",
    "RechtsFundament",
    "GrundsatzRegister",
    "RegisterEintrag",
    "RegisterKategorie",
    "RegisterProzedur",
    "RegisterStatus",
    "PrinzipienKlasse",
    "PrinzipienKodex",
    "PrinzipienProzedur",
    "PrinzipienSatz",
    "PrinzipienStatus",
    "WerteArtikel",
    "WerteCharta",
    "WerteProzedur",
    "WerteStatus",
    "WerteTyp",
    "KonventBeschluss",
    "KonventProzedur",
    "LeitbildAusrichtung",
    "LeitbildKonvent",
    "LeitbildResolution",
    "MissionsArtikel",
    "MissionsRang",
    "MissionsVerfassung",
    "VerfassungsProzedur",
    "VerfassungsStatus",
    "ManifestGeltung",
    "ManifestProzedur",
    "ZweckDimension",
    "ZweckKlausel",
    "ZweckManifest",
    "KonstitutionsArtikel",
    "KonstitutionsEbene",
    "KonstitutionsProzedur",
    "KonstitutionsRang",
    "LeitsternKonstitution",
    "GrundgesetzGeltung",
    "GrundgesetzParagraph",
    "GrundgesetzProzedur",
    "GrundgesetzTitel",
    "VerfassungsGrundgesetz",
    "StaatsEbene",
    "StaatsGeltung",
    "StaatsNorm",
    "StaatsOrdnung",
    "StaatsProzedur",
    "KodexKlasse",
    "KodexNorm",
    "KodexProzedur",
    "KodexStatus",
    "RechtsKodex",
    "UnionsAkt",
    "UnionsGeltung",
    "UnionsNorm",
    "UnionsProzedur",
    "UnionsTyp",
    "FoederalGeltung",
    "FoederalNorm",
    "FoederalProzedur",
    "FoederalTyp",
    "FoederalVertrag",
    "BundesCharta",
    "BundesGeltung",
    "BundesNorm",
    "BundesProzedur",
    "BundesRang",
    "HoheitsGeltung",
    "HoheitsGrad",
    "HoheitsManifest",
    "HoheitsNorm",
    "HoheitsProzedur",
    "SuprematsGeltung",
    "SuprematsKlasse",
    "SuprematsNorm",
    "SuprematsProzedur",
    "SuprematsRegister",
    "EwigkeitsGeltung",
    "EwigkeitsNorm",
    "EwigkeitsProzedur",
    "GrundrechtsSenat",
    "SenatGeltung",
    "SenatNorm",
    "SenatProzedur",
    "SenatRang",
    "VerfassungsKodex",
    "VerfassungsKodexGeltung",
    "VerfassungsKodexNorm",
    "VerfassungsKodexProzedur",
    "VerfassungsKodexRang",
    "WeltordnungsEbene",
    "WeltordnungsGeltung",
    "WeltordnungsNorm",
    "WeltordnungsPrinzip",
    "WeltordnungsProzedur",
    "VoelkerrechtsGeltung",
    "VoelkerrechtsKlasse",
    "VoelkerrechtsKodex",
    "VoelkerrechtsNorm",
    "VoelkerrechtsProzedur",
    "DiplomatieCharta",
    "DiplomatieGeltung",
    "DiplomatieNorm",
    "DiplomatieProzedur",
    "DiplomatieRang",
    "AllianzGeltung",
    "AllianzNorm",
    "AllianzProzedur",
    "AllianzTyp",
    "AllianzVertrag",
    "KooperationsGeltung",
    "KooperationsGrad",
    "KooperationsManifest",
    "KooperationsNorm",
    "KooperationsProzedur",
    "SolidaritaetsGeltung",
    "SolidaritaetsNorm",
    "SolidaritaetsPakt",
    "SolidaritaetsProzedur",
    "SolidaritaetsTyp",
    "UniversalrechtsGeltung",
    "UniversalrechtsNorm",
    "UniversalrechtsProzedur",
    "UniversalrechtsRang",
    "UniversalrechtsRegister",
    "KosmosEbene",
    "KosmosGeltung",
    "KosmosNorm",
    "KosmosNormEintrag",
    "KosmosProzedur",
    "WeltgeistGeltung",
    "WeltgeistProzedur",
    "WeltgeistRang",
    "WeltgeistSenat",
    "WeltgeistSitz",
    "UniversalKodex",
    "UniversalKodexGeltung",
    "UniversalKodexKlasse",
    "UniversalKodexNorm",
    "UniversalKodexProzedur",
    "UrsprungsCharta",
    "UrsprungsGeltung",
    "UrsprungsNorm",
    "UrsprungsProzedur",
    "UrsprungsTyp",
    "SchoepfungsGeltung",
    "SchoepfungsGrad",
    "SchoepfungsNorm",
    "SchoepfungsProzedur",
    "SchoepfungsVertrag",
    "ErbeGeltung",
    "ErbeKlasse",
    "ErbeNorm",
    "ErbeProzedur",
    "ErbeRegister",
    "ZivilisationsGeltung",
    "ZivilisationsNorm",
    "ZivilisationsPakt",
    "ZivilisationsProzedur",
    "ZivilisationsTyp",
    "KulturgutGeltung",
    "KulturgutKodex",
    "KulturgutNorm",
    "KulturgutProzedur",
    "KulturgutRang",
    "WissensGeltung",
    "WissensGrad",
    "WissensManifest",
    "WissensNorm",
    "WissensProzedur",
    "GedaechtnisGeltung",
    "GedaechtnisNorm",
    "GedaechtnisProzedur",
    "GedaechtnisRang",
    "GedaechtnisSenat",
    "WeisheitsEbene",
    "WeisheitsGeltung",
    "WeisheitsNorm",
    "WeisheitsNormEintrag",
    "WeisheitsProzedur",
    "ErkenntnisCharta",
    "ErkenntnisGeltung",
    "ErkenntnisNorm",
    "ErkenntnisProzedur",
    "ErkenntnisTyp",
    "TranszendenzEbene",
    "TranszendenzGeltung",
    "TranszendenzKodex",
    "TranszendenzNorm",
    "TranszendenzProzedur",
    "AxiomGeltung",
    "AxiomProzedur",
    "AxiomRang",
    "UrsprungsAxiom",
    "UrsprungsAxiomEintrag",
    "SeinsCharta",
    "SeinsGeltung",
    "SeinsNorm",
    "SeinsProzedur",
    "SeinsTyp",
    "WirklichkeitsEbene",
    "WirklichkeitsGeltung",
    "WirklichkeitsKodex",
    "WirklichkeitsNorm",
    "WirklichkeitsProzedur",
    "KausalitaetsGeltung",
    "KausalitaetsNorm",
    "KausalitaetsProzedur",
    "KausalitaetsRang",
    "KausalitaetsRegister",
    "KosmosEwigkeit",
    "KosmosEwigkeitsGeltung",
    "KosmosEwigkeitsNormEintrag",
    "KosmosEwigkeitsProzedur",
    "KosmosEwigkeitsRang",
    "AbsolutCharta",
    "AbsolutGeltung",
    "AbsolutNorm",
    "AbsolutProzedur",
    "AbsolutTyp",
    "KosmosVerfassung",
    "KosmosVerfassungsGeltung",
    "KosmosVerfassungsNorm",
    "KosmosVerfassungsProzedur",
    "KosmosVerfassungsTyp",
    "QuantenFeld",
    "QuantenFeldGeltung",
    "QuantenFeldNorm",
    "QuantenFeldProzedur",
    "QuantenFeldTyp",
    "DimensionsGeltung",
    "DimensionsNorm",
    "DimensionsProzedur",
    "DimensionsRang",
    "DimensionsRegister",
    "WellenCharta",
    "WellenGeltung",
    "WellenNorm",
    "WellenProzedur",
    "WellenTyp",
    "SuperpositionsGeltung",
    "SuperpositionsKodex",
    "SuperpositionsNorm",
    "SuperpositionsProzedur",
    "SuperpositionsTyp",
    "VerschraenkunsGeltung",
    "VerschraenkunsNorm",
    "VerschraenkunsPakt",
    "VerschraenkunsProzedur",
    "VerschraenkunsTyp",
    "KollapsGeltung",
    "KollapsManifest",
    "KollapsNorm",
    "KollapsProzedur",
    "KollapsTyp",
    "QuantenSenat",
    "QuantenSenatGeltung",
    "QuantenSenatNorm",
    "QuantenSenatProzedur",
    "QuantenSenatTyp",
    "PlanckGeltung",
    "PlanckNorm",
    "PlanckNormEintrag",
    "PlanckProzedur",
    "PlanckTyp",
    "StringtheorieCharta",
    "StringtheorieGeltung",
    "StringtheorieNorm",
    "StringtheorieProzedur",
    "StringtheorieTyp",
    "QuantenVerfassung",
    "QuantenVerfassungsGeltung",
    "QuantenVerfassungsNorm",
    "QuantenVerfassungsProzedur",
    "QuantenVerfassungsTyp",
    "RelativitaetsFeld",
    "RelativitaetsGeltung",
    "RelativitaetsNorm",
    "RelativitaetsProzedur",
    "RelativitaetsTyp",
    "RaumzeitGeltung",
    "RaumzeitNorm",
    "RaumzeitProzedur",
    "RaumzeitRang",
    "RaumzeitRegister",
    "LichtgeschwindigkeitsCharta",
    "LichtgeschwindigkeitsGeltung",
    "LichtgeschwindigkeitsNorm",
    "LichtgeschwindigkeitsProzedur",
    "LichtgeschwindigkeitsTyp",
    "GravitationsGeltung",
    "GravitationsKodex",
    "GravitationsNorm",
    "GravitationsProzedur",
    "GravitationsTyp",
    "KruemmungsGeltung",
    "KruemmungsNorm",
    "KruemmungsPakt",
    "KruemmungsProzedur",
    "KruemmungsTyp",
    "SingularitaetsGeltung",
    "SingularitaetsManifest",
    "SingularitaetsNorm",
    "SingularitaetsProzedur",
    "SingularitaetsTyp",
    "SchwarzeLoechSenat",
    "SchwarzsLochGeltung",
    "SchwarzsLochNorm",
    "SchwarzsLochProzedur",
    "SchwarzsLochTyp",
    "EreignishorizontGeltung",
    "EreignishorizontNorm",
    "EreignishorizontNormEintrag",
    "EreignishorizontProzedur",
    "EreignishorizontTyp",
    "ZeitdilatationsCharta",
    "ZeitdilatationsGeltung",
    "ZeitdilatationsNorm",
    "ZeitdilatationsProzedur",
    "ZeitdilatationsTyp",
    "RelativitaetsGeltung",
    "RelativitaetsNorm",
    "RelativitaetsProzedur",
    "RelativitaetsTyp",
    "RelativitaetsVerfassung",
    "ThermodynamikFeld",
    "ThermodynamikGeltung",
    "ThermodynamikNorm",
    "ThermodynamikProzedur",
    "ThermodynamikTyp",
    "EntropieGeltung",
    "EntropieNorm",
    "EntropieRegister",
    "EntropieProzedur",
    "EntropieTyp",
    "WaermeCharta",
    "WaermeGeltung",
    "WaermeNorm",
    "WaermeProzedur",
    "WaermeTyp",
    "EnergieerhaltungsGeltung",
    "EnergieerhaltungsKodex",
    "EnergieerhaltungsNorm",
    "EnergieerhaltungsProzedur",
    "EnergieerhaltungsTyp",
    "GleichgewichtsGeltung",
    "GleichgewichtsNorm",
    "GleichgewichtsPakt",
    "GleichgewichtsProzedur",
    "GleichgewichtsTyp",
    "CarnotGeltung",
    "CarnotManifest",
    "CarnotNorm",
    "CarnotProzedur",
    "CarnotTyp",
    "BoltzmannGeltung",
    "BoltzmannNorm",
    "BoltzmannSenat",
    "BoltzmannProzedur",
    "BoltzmannTyp",
    "EntropieNormEintrag",
    "EntropieNormGeltung",
    "EntropieNormProzedur",
    "EntropieNormSatz",
    "EntropieNormTyp",
    "WaermestrahlungsCharta",
    "WaermestrahlungsGeltung",
    "WaermestrahlungsNorm",
    "WaermestrahlungsProzedur",
    "WaermestrahlungsTyp",
    "ThermodynamikVerfassung",
    "ThermoverfassungsGeltung",
    "ThermoverfassungsNorm",
    "ThermoverfassungsProzedur",
    "ThermoverfassungsTyp",
    "EinheitsGeltung",
    "EinheitsNorm",
    "EinheitsProzedur",
    "EinheitsSenat",
    "EinheitsTyp",
    "HarmonieGeltung",
    "HarmonieNorm",
    "HarmoniePakt",
    "HarmonieProzedur",
    "HarmonieTyp",
    "KosmosOrdnung",
    "KosmosOrdnungsGeltung",
    "KosmosOrdnungsNorm",
    "KosmosOrdnungsProzedur",
    "KosmosOrdnungsTyp",
    "ExceptionCase",
    "ExceptionKind",
    "ExceptionRegister",
    "ExceptionSeverity",
    "FederationAlignmentStatus",
    "FederationCell",
    "FederationCoordination",
    "FederationDomain",
    "FederationHandoff",
    "FederationHandoffPriority",
    "GovernanceAgenda",
    "GovernanceAgendaItem",
    "GovernanceAgendaStatus",
    "GateDecision",
    "GateReadiness",
    "GateState",
    "GateOutcome",
    "Guardrail",
    "GuardrailDomain",
    "GuardrailPolicyMode",
    "GuardrailPortfolio",
    "HandoffMode",
    "HumanDecision",
    "HumanLoopGovernance",
    "IdentityKind",
    "ImprovementExecutionMode",
    "ImprovementOrchestrator",
    "ImprovementPriority",
    "ImprovementWave",
    "IncidentCause",
    "IncidentReport",
    "IncidentSeverity",
    "IntegratedOperationsRun",
    "IntegratedSmokeBuild",
    "InterventionFallback",
    "InterventionMode",
    "InterventionSimulation",
    "InterventionSimulationStatus",
    "InterventionSimulator",
    "LearningPatternType",
    "LearningRecord",
    "LearningRegister",
    "LoadedControlPlane",
    "MissionPolicy",
    "MissionProfile",
    "MissionScenario",
    "ModuleBoundary",
    "ModuleBoundaryName",
    "OperationalPressure",
    "OperationsWave",
    "OperationsRunLedger",
    "OperationsIncident",
    "OperationsCockpit",
    "OperationsSteward",
    "OperationsStewardStatus",
    "OutcomeLedger",
    "OutcomeRecord",
    "OutcomeStatus",
    "OperatingConstitution",
    "OperatingMode",
    "OrchestrationState",
    "OrchestrationStatus",
    "ConstitutionArticle",
    "ConstitutionPrinciple",
    "ConstitutionalAuthority",
    "PlaybookCatalog",
    "PlaybookEntry",
    "PlaybookReadiness",
    "PlaybookType",
    "PortfolioAction",
    "PortfolioOptimizer",
    "PortfolioPriority",
    "PortfolioRecommendation",
    "PolicyTuneAction",
    "PolicyTuneEntry",
    "PolicyTuner",
    "ProgramController",
    "ProgramControllerStatus",
    "ProgramDirective",
    "ProgramTrack",
    "ProgramTrackType",
    "PermissionRule",
    "PersistenceRecord",
    "PressureLevel",
    "ProtocolContext",
    "ReadinessCadence",
    "ReadinessCadenceEntry",
    "ReadinessCadenceStatus",
    "ReadinessCadenceTrigger",
    "ReadinessCadenceWindow",
    "ReadinessFinding",
    "ReadinessFindingSeverity",
    "ReadinessReview",
    "RecoveryCheckpoint",
    "RecoveryDrill",
    "RecoveryDrillStatus",
    "RecoveryDrillSuite",
    "RemediationCampaign",
    "RemediationCampaignStage",
    "RemediationCampaignStageType",
    "RemediationCampaignStatus",
    "ReleaseCampaign",
    "ReleaseCampaignStage",
    "ReleaseCampaignStageType",
    "ReleaseCampaignStatus",
    "ReviewActionItem",
    "ReviewActionPlan",
    "ReviewActionPriority",
    "ReviewActionType",
    "RecoveryDisposition",
    "RecoveryMode",
    "RecoveryOrchestration",
    "RecoveryOutcome",
    "RiskImpact",
    "RiskLikelihood",
    "RiskMitigationStatus",
    "RiskRecord",
    "RiskRegister",
    "ReplayMode",
    "RoleName",
    "RolloutPhase",
    "RolloutState",
    "RollbackDirective",
    "RuntimeDNA",
    "RuntimeHooks",
    "RuntimeIdentity",
    "RuntimeScorecard",
    "RuntimeScorecardEntry",
    "RuntimeStage",
    "RuntimeThresholds",
    "RunLedgerEntry",
    "PreviewMode",
    "ScenarioReplayItem",
    "ScenarioReplayResult",
    "ScenarioReplaySuite",
    "ShadowCoordination",
    "ShadowCoordinationMode",
    "StewardDirective",
    "StewardDirectiveType",
    "StewardWorkboard",
    "ShadowPreview",
    "TelemetryAlert",
    "TelemetrySignal",
    "TelemetrySnapshot",
    "TransferEnvelope",
    "TrustLevel",
    "ValidationStep",
    "WaveBudgetPolicy",
    "WaveMissionExecution",
    "WorkboardItem",
    "WorkboardLane",
    "WorkboardQueue",
    "WorkboardStatus",
    "WorkClaim",
    "WorkCostProfile",
    "WorkHandoff",
    "WorkPriority",
    "WorkStatus",
    "WorkUnit",
    "authorize_action",
    "authorize_artifact",
    "advance_orchestration_state",
    "advance_rollout_state",
    "advance_work_unit",
    "audit_entry_for_artifact",
    "audit_entry_for_message",
    "benchmark_case_matrix",
    "build_autonomy_governor",
    "build_capacity_planner",
    "build_continuous_readiness_cycle",
    "build_convergence_simulator",
    "build_dispatch_plan",
    "build_drift_monitor",
    "build_escalation_router",
    "build_evidence_ledger",
    "build_executive_watchtower",
    "build_strategy_council",
    "build_mandate_card_deck",
    "build_portfolio_radar",
    "build_scenario_chancery",
    "build_course_corrector",
    "build_mandate_memory_store",
    "build_guideline_compass",
    "build_intervention_charter",
    "build_program_senate",
    "build_directive_consensus",
    "build_decision_archive",
    "build_execution_cabinet",
    "build_delegation_matrix",
    "build_veto_sluice",
    "build_consensus_diplomacy",
    "build_leitstern_doctrine",
    "build_missions_collegium",
    "build_priority_conclave",
    "build_course_contract",
    "build_leitstern_codex",
    "build_kodex_register",
    "build_satzungs_rat",
    "build_mandats_konvent",
    "build_normen_tribunal",
    "build_verfassungs_senat",
    "build_grundrechts_charta",
    "build_souveraenitaets_akt",
    "build_ordnungs_manifest",
    "build_leitordnung",
    "build_autoritaets_dekret",
    "build_rechts_fundament",
    "build_grundsatz_register",
    "build_prinzipien_kodex",
    "build_werte_charta",
    "build_leitbild_konvent",
    "build_missions_verfassung",
    "build_zweck_manifest",
    "build_leitstern_konstitution",
    "build_verfassungs_grundgesetz",
    "build_staats_ordnung",
    "build_rechts_kodex",
    "build_unions_akt",
    "build_foederal_vertrag",
    "build_bundes_charta",
    "build_hoheits_manifest",
    "build_supremats_register",
    "build_ewigkeits_norm",
    "build_grundrechts_senat",
    "build_verfassungs_kodex",
    "build_weltordnungs_prinzip",
    "build_voelkerrechts_kodex",
    "build_diplomatie_charta",
    "build_allianz_vertrag",
    "build_kooperations_manifest",
    "build_solidaritaets_pakt",
    "build_universalrechts_register",
    "build_kosmos_norm",
    "build_weltgeist_senat",
    "build_universal_kodex",
    "build_ursprungs_charta",
    "build_schoepfungs_vertrag",
    "build_erbe_register",
    "build_zivilisations_pakt",
    "build_kulturgut_kodex",
    "build_wissens_manifest",
    "build_gedaechtnis_senat",
    "build_weisheits_norm",
    "build_erkenntnis_charta",
    "build_transzendenz_kodex",
    "build_ursprungs_axiom",
    "build_seins_charta",
    "build_wirklichkeits_kodex",
    "build_kausalitaets_register",
    "build_kosmos_ordnung",
    "build_harmonie_pakt",
    "build_einheits_senat",
    "build_kosmos_ewigkeit",
    "build_absolut_charta",
    "build_kosmos_verfassung",
    "build_quanten_feld",
    "build_dimensions_register",
    "build_wellen_charta",
    "build_superpositions_kodex",
    "build_verschraenkungs_pakt",
    "build_kollaps_manifest",
    "build_quanten_senat",
    "build_planck_norm",
    "build_stringtheorie_charta",
    "build_quanten_verfassung",
    "build_relativitaets_feld",
    "build_raumzeit_register",
    "build_lichtgeschwindigkeits_charta",
    "build_gravitations_kodex",
    "build_kruemmungs_pakt",
    "build_singularitaets_manifest",
    "build_schwarzes_loch_senat",
    "build_ereignishorizont_norm",
    "build_zeitdilatations_charta",
    "build_relativitaets_verfassung",
    "build_thermodynamik_feld",
    "build_entropie_register",
    "build_waerme_charta",
    "build_energieerhaltungs_kodex",
    "build_gleichgewichts_pakt",
    "build_carnot_manifest",
    "build_boltzmann_senat",
    "build_entropie_norm",
    "build_waermestrahlung_charta",
    "build_thermodynamik_verfassung",
    "build_elektromagnetik_feld",
    "build_ladungs_register",
    "build_maxwell_charta",
    "build_induktions_kodex",
    "build_wellenausbreitung_pakt",
    "build_lichtgeschwindigkeits_manifest",
    "build_spektral_senat",
    "build_photon_norm",
    "build_photoeffekt_charta",
    "build_elektromagnetik_verfassung",
    "build_kernphysik_feld",
    "build_nukleon_register",
    "build_stark_charta",
    "build_schwach_kodex",
    "build_kernspaltungs_pakt",
    "build_kernfusions_manifest",
    "build_radioaktivitaets_senat",
    "build_zerfalls_norm",
    "build_nuklear_charta",
    "build_kernphysik_verfassung",
    "build_teilchen_feld",
    "build_quark_register",
    "build_lepton_charta",
    "build_gluon_kodex",
    "build_eichboson_pakt",
    "build_higgs_manifest",
    "build_symmetriebrechungs_senat",
    "build_feynman_norm",
    "build_standardmodell_charta",
    "build_teilchenphysik_verfassung",
    "build_kosmologie_feld",
    "build_urknall_register",
    "build_inflation_charta",
    "build_dunkle_materie_kodex",
    "build_dunkle_energie_pakt",
    "build_cmb_manifest",
    "build_strukturbildungs_senat",
    "build_expansion_norm",
    "build_hubble_charta",
    "build_kosmologie_verfassung",
    "build_astrophysik_feld",
    "build_protostellar_register",
    "build_hauptreihen_charta",
    "build_fusionsreaktor_kodex",
    "build_roter_riese_pakt",
    "build_supernova_manifest",
    "build_neutronenstern_senat",
    "build_schwarzes_loch_norm",
    "build_hertzsprung_russell_charta",
    "build_astrophysik_verfassung",
    "build_festkoerper_feld",
    "build_kristallgitter_register",
    "build_bandstruktur_charta",
    "build_halbleiter_kodex",
    "build_supraleitung_pakt",
    "build_quanten_hall_manifest",
    "build_phonon_senat",
    "build_fermi_norm",
    "build_bose_einstein_charta",
    "build_festkoerper_verfassung",
    "build_plasma_feld",
    "build_magnetohydrodynamik_register",
    "build_debye_abschirmung_charta",
    "build_alfven_wellen_kodex",
    "build_z_pinch_pakt",
    "build_tokamak_manifest",
    "build_traegheitsfusion_senat",
    "build_plasmawellen_norm",
    "build_kernfusion_charta",
    "build_plasma_verfassung",
    "build_lorenz_attraktor_feld",
    "build_bifurkations_register",
    "build_lyapunov_kodex",
    "build_fraktal_charta",
    "build_strange_attraktor_pakt",
    "build_emergenz_senat",
    "build_perkolations_norm",
    "build_komplexitaets_charta",
    "build_adaptiv_schwarm_kodex",
    "build_chaos_verfassung",
    "build_shannon_entropie_feld",
    "build_kanalkapazitaet_register",
    "build_quanten_bit_kodex",
    "build_verschraenkung_charta",
    "build_quantenfehler_pakt",
    "build_quantenkrypto_senat",
    "build_holographisches_prinzip_norm",
    "build_landauer_manifest",
    "NoCloningGeltung",
    "NoCloningKodex",
    "NoCloningNorm",
    "NoCloningProzedur",
    "NoCloningTyp",
    "build_no_cloning_kodex",
    "QuanteninformationsVerfassung",
    "QuanteninformationsVerfassungsGeltung",
    "QuanteninformationsVerfassungsNorm",
    "QuanteninformationsVerfassungsProzedur",
    "QuanteninformationsVerfassungsTyp",
    "build_quanteninformations_verfassung",
    "BiophysikFeld",
    "BiophysikGeltung",
    "BiophysikNorm",
    "BiophysikProzedur",
    "BiophysikTyp",
    "build_biophysik_feld",
    "DnaReplikationGeltung",
    "DnaReplikationNorm",
    "DnaReplikationProzedur",
    "DnaReplikationRegister",
    "DnaReplikationTyp",
    "build_dna_replikation_register",
    "ProteinfaltungCharta",
    "ProteinfaltungGeltung",
    "ProteinfaltungNorm",
    "ProteinfaltungProzedur",
    "ProteinfaltungTyp",
    "build_proteinfaltung_charta",
    "HodgkinHuxleyGeltung",
    "HodgkinHuxleyKodex",
    "HodgkinHuxleyNorm",
    "HodgkinHuxleyProzedur",
    "HodgkinHuxleyTyp",
    "build_hodgkin_huxley_kodex",
    "SynaptischePlastizitaetGeltung",
    "SynaptischePlastizitaetNorm",
    "SynaptischePlastizitaetPakt",
    "SynaptischePlastizitaetProzedur",
    "SynaptischePlastizitaetTyp",
    "build_synaptische_plastizitaet_pakt",
    "EvolutionGeltung",
    "EvolutionManifest",
    "EvolutionNorm",
    "EvolutionProzedur",
    "EvolutionTyp",
    "build_evolution_manifest",
    "HomoostaseGeltung",
    "HomoostaseNorm",
    "HomoostaseSenat",
    "HomoostaseTyp",
    "HomoostasProzedur",
    "build_homoostase_senat",
    "LotkaVolterraNormEintrag",
    "LotkaVolterraNormGeltung",
    "LotkaVolterraNormProzedur",
    "LotkaVolterraNormSatz",
    "LotkaVolterraNormTyp",
    "build_lotka_volterra_norm",
    "MorphogeneseCharta",
    "MorphogeneseGeltung",
    "MorphogeneseNorm",
    "MorphogeneseProzedur",
    "MorphogeneseTyp",
    "build_morphogenese_charta",
    "SystembiologieVerfassung",
    "SystembiologieVerfassungsGeltung",
    "SystembiologieVerfassungsNorm",
    "SystembiologieVerfassungsProzedur",
    "SystembiologieVerfassungsTyp",
    "build_systembiologie_verfassung",
    "KognitionsFeld",
    "KognitionsGeltung",
    "KognitionsNorm",
    "KognitionsProzedur",
    "KognitionsTyp",
    "build_kognitions_feld",
    "ArbeitsgedaechtnisGeltung",
    "ArbeitsgedaechtnisNorm",
    "ArbeitsgedaechtnisRegister",
    "ArbeitsgedaechtnisTyp",
    "ArbeitsgedaechtnispProzedur",
    "build_arbeitsgedaechtnis_register",
    "AufmerksamkeitsCharta",
    "AufmerksamkeitsGeltung",
    "AufmerksamkeitsNorm",
    "AufmerksamkeitsProzedur",
    "AufmerksamkeitsTyp",
    "build_aufmerksamkeits_charta",
    "EntscheidungsGeltung",
    "EntscheidungsKodex",
    "EntscheidungsNorm",
    "EntscheidungsProzedur",
    "EntscheidungsTyp",
    "build_entscheidungs_kodex",
    "GedaechtnisKonsolidierungsGeltung",
    "GedaechtnisKonsolidierungsNorm",
    "GedaechtnisKonsolidierungsPakt",
    "GedaechtnisKonsolidierungsProzedur",
    "GedaechtnisKonsolidierungsTyp",
    "build_gedaechtnis_konsolidierungs_pakt",
    "SprachverarbeitungsGeltung",
    "SprachverarbeitungsManifest",
    "SprachverarbeitungsNorm",
    "SprachverarbeitungsProzedur",
    "SprachverarbeitungsTyp",
    "build_sprachverarbeitungs_manifest",
    "BewusstseinsGeltung",
    "BewusstseinsNorm",
    "BewusstseinsSenat",
    "BewusstseinsTyp",
    "BewusstseinsProzedur",
    "build_bewusstseins_senat",
    "MetakognitionsNormEintrag",
    "MetakognitionsNormGeltung",
    "MetakognitionsNormProzedur",
    "MetakognitionsNormSatz",
    "MetakognitionsNormTyp",
    "build_metakognitions_norm",
    "KognitiveFlexibilitaetsCharta",
    "KognitiveFlexibilitaetsGeltung",
    "KognitiveFlexibilitaetsNorm",
    "KognitiveFlexibilitaetsProzedur",
    "KognitiveFlexibilitaetsTyp",
    "build_kognitive_flexibilitaets_charta",
    "KognitionsVerfassung",
    "KognitionsVerfassungsGeltung",
    "KognitionsVerfassungsNorm",
    "KognitionsVerfassungsProzedur",
    "KognitionsVerfassungsTyp",
    "build_kognitions_verfassung",
    "MathematikFeld",
    "MathematikFeldGeltung",
    "MathematikFeldNorm",
    "MathematikFeldProzedur",
    "MathematikFeldTyp",
    "build_mathematik_feld",
    "MengenRegister",
    "MengenRegisterGeltung",
    "MengenRegisterNorm",
    "MengenRegisterProzedur",
    "MengenRegisterTyp",
    "build_mengen_register",
    "LogikCharta",
    "LogikChartaGeltung",
    "LogikChartaNorm",
    "LogikChartaProzedur",
    "LogikChartaTyp",
    "build_logik_charta",
    "WahrscheinlichkeitsKodex",
    "WahrscheinlichkeitsKodexGeltung",
    "WahrscheinlichkeitsKodexNorm",
    "WahrscheinlichkeitsKodexProzedur",
    "WahrscheinlichkeitsKodexTyp",
    "build_wahrscheinlichkeits_kodex",
    "SpieltheoriePakt",
    "SpieltheoriePaktGeltung",
    "SpieltheoriePaktNorm",
    "SpieltheoriePaktProzedur",
    "SpieltheoriePaktTyp",
    "build_spieltheorie_pakt",
    "GraphenManifest",
    "GraphenManifestGeltung",
    "GraphenManifestNorm",
    "GraphenManifestProzedur",
    "GraphenManifestTyp",
    "build_graphen_manifest",
    "AlgorithmenSenat",
    "AlgorithmenSenatGeltung",
    "AlgorithmenSenatNorm",
    "AlgorithmenSenatProzedur",
    "AlgorithmenSenatTyp",
    "build_algorithmen_senat",
    "GodelNormEintrag",
    "GodelNormGeltung",
    "GodelNormProzedur",
    "GodelNormSatz",
    "GodelNormTyp",
    "build_godel_norm",
    "TopologieCharta",
    "TopologieChartaGeltung",
    "TopologieChartaNorm",
    "TopologieChartaProzedur",
    "TopologieChartaTyp",
    "build_topologie_charta",
    "MathematikVerfassung",
    "MathematikVerfassungsGeltung",
    "MathematikVerfassungsNorm",
    "MathematikVerfassungsProzedur",
    "MathematikVerfassungsTyp",
    "build_mathematik_verfassung",
    "EmergenzFeld",
    "EmergenzFeldGeltung",
    "EmergenzFeldNorm",
    "EmergenzFeldProzedur",
    "EmergenzFeldTyp",
    "build_emergenz_feld",
    "DissipativeStrukturenRegister",
    "DissipativeStrukturenRegisterGeltung",
    "DissipativeStrukturenRegisterNorm",
    "DissipativeStrukturenRegisterProzedur",
    "DissipativeStrukturenRegisterTyp",
    "build_dissipative_strukturen_register",
    "KritikalitaetsCharta",
    "KritikalitaetsChartaGeltung",
    "KritikalitaetsChartaNorm",
    "KritikalitaetsChartaProzedur",
    "KritikalitaetsChartaTyp",
    "build_kritikalitaets_charta",
    "FraktalKodex",
    "FraktalKodexGeltung",
    "FraktalKodexNorm",
    "FraktalKodexProzedur",
    "FraktalKodexTyp",
    "build_fraktal_kodex",
    "ZellulaereAutomatenPakt",
    "ZellulaereAutomatenPaktGeltung",
    "ZellulaereAutomatenPaktNorm",
    "ZellulaereAutomatenPaktProzedur",
    "ZellulaereAutomatenPaktTyp",
    "build_zellulaere_automaten_pakt",
    "FitnessLandschaftManifest",
    "FitnessLandschaftManifestGeltung",
    "FitnessLandschaftManifestNorm",
    "FitnessLandschaftManifestProzedur",
    "FitnessLandschaftManifestTyp",
    "build_fitness_landschaft_manifest",
    "AdaptiveSystemeSenat",
    "AdaptiveSystemeSenatGeltung",
    "AdaptiveSystemeSenatNorm",
    "AdaptiveSystemeSenatProzedur",
    "AdaptiveSystemeSenatTyp",
    "build_adaptive_systeme_senat",
    "SynergetikNormSatz",
    "SynergetikNormGeltung",
    "SynergetikNormEintrag",
    "SynergetikNormProzedur",
    "SynergetikNormTyp",
    "build_synergetik_norm",
    "KuenstlichesLebenCharta",
    "KuenstlichesLebenChartaGeltung",
    "KuenstlichesLebenChartaNorm",
    "KuenstlichesLebenChartaProzedur",
    "KuenstlichesLebenChartaTyp",
    "build_kuenstliches_leben_charta",
    "KomplexeSystemeVerfassung",
    "KomplexeSystemeVerfassungsGeltung",
    "KomplexeSystemeVerfassungsNorm",
    "KomplexeSystemeVerfassungsProzedur",
    "KomplexeSystemeVerfassungsTyp",
    "build_komplexe_systeme_verfassung",
    "InformationsFeldGeltung", "InformationsFeldNorm", "InformationsFeldProzedur",
    "InformationsFeldTyp", "InformationsFeld", "build_informations_feld",
    "KanalRegisterGeltung", "KanalRegisterNorm", "KanalRegisterProzedur",
    "KanalRegisterTyp", "KanalRegister", "build_kanal_register",
    "KybernetikChartaGeltung", "KybernetikChartaNorm", "KybernetikChartaProzedur",
    "KybernetikChartaTyp", "KybernetikCharta", "build_kybernetik_charta",
    "RegelkreisKodexGeltung", "RegelkreisKodexNorm", "RegelkreisKodexProzedur",
    "RegelkreisKodexTyp", "RegelkreisKodex", "build_regelkreis_kodex",
    "EntropiePaktGeltung", "EntropiePaktNorm", "EntropiePaktProzedur",
    "EntropiePaktTyp", "EntropiePakt", "build_entropie_pakt",
    "SelbstregulationsManifestGeltung", "SelbstregulationsManifestNorm", "SelbstregulationsManifestProzedur",
    "SelbstregulationsManifestTyp", "SelbstregulationsManifest", "build_selbstregulations_manifest",
    "RueckkopplungsSenatGeltung", "RueckkopplungsSenatNorm", "RueckkopplungsSenatProzedur",
    "RueckkopplungsSenatTyp", "RueckkopplungsSenat", "build_rueckkopplungs_senat",
    "KybernetikNormGeltung", "KybernetikNormEintrag", "KybernetikNormProzedur",
    "KybernetikNormTyp", "KybernetikNormSatz", "build_kybernetik_norm",
    "KomplexitaetsSteuerungsChartaGeltung", "KomplexitaetsSteuerungsChartaNorm", "KomplexitaetsSteuerungsChartaProzedur",
    "KomplexitaetsSteuerungsChartaTyp", "KomplexitaetsSteuerungsCharta", "build_komplexitaets_steuerungs_charta",
    "InformationsVerfassungsGeltung", "InformationsVerfassungsNorm", "InformationsVerfassungsProzedur",
    "InformationsVerfassungsTyp", "InformationsVerfassung", "build_informations_verfassung",
    "build_exception_register",
    "build_federation_coordination",
    "build_governance_agenda",
    "build_improvement_orchestrator",
    "build_intervention_simulator",
    "build_learning_register",
    "build_operations_cockpit",
    "build_operations_steward",
    "build_operating_constitution",
    "build_outcome_ledger",
    "build_playbook_catalog",
    "build_portfolio_optimizer",
    "build_policy_tuner",
    "build_program_controller",
    "build_remediation_campaign",
    "build_release_campaign",
    "build_readiness_cadence",
    "build_readiness_review",
    "build_recovery_drill_suite",
    "build_review_action_plan",
    "build_risk_register",
    "build_scenario_replay",
    "build_runtime_scorecard",
    "build_steward_workboard",
    "build_telemetry_snapshot",
    "claim_for_work_unit",
    "coordinate_escalations",
    "command_message",
    "coordinate_shadow_work",
    "correlate_operation",
    "core_state_for_runtime",
    "detect_incidents",
    "evaluate_dry_run",
    "dispatch_signal",
    "event_message",
    "evaluate_gate",
    "evidence_message",
    "govern_recovery_orchestration",
    "build_guardrail_portfolio",
    "dispatch_priority_score",
    "gate_signal",
    "load_control_plane",
    "ledger_for_wave",
    "module_boundaries",
    "module_boundary",
    "module_dependency_graph",
    "mission_profile_catalog",
    "mission_profile_for_name",
    "operation_alerts",
    "open_change_window",
    "orchestration_state_for_runtime",
    "orchestrate_recovery_for_rollout",
    "permission_catalog",
    "protocol_context",
    "role_permissions",
    "rollout_state_for_shadow",
    "run_benchmark_harness",
    "run_integrated_smoke_build",
    "recovery_checkpoint_for_state",
    "recovery_outcome",
    "rollback_directive_for_checkpoint",
    "runtime_dna_for_profile",
    "runtime_dna_from_env",
    "shadow_event",
    "shadow_preview_for_command",
    "shadow_snapshot",
    "telemetry_alert",
    "telemetry_signal_from_event",
    "handoff_for_work_unit",
    "transfer_message",
    "transfer_envelope_for_state",
    "work_unit_for_state",
    "run_integrated_operations",
    "run_operations_wave",
    # Block #491–#500: Soziologie & Gesellschaftstheorie
    "SoziologieFeldGeltung", "SoziologieFeldNorm", "SoziologieFeldProzedur", "SoziologieFeldTyp",
    "SoziologieFeld", "build_soziologie_feld",
    "GesellschaftsRegisterGeltung", "GesellschaftsRegisterNorm", "GesellschaftsRegisterProzedur", "GesellschaftsRegisterTyp",
    "GesellschaftsRegister", "build_gesellschafts_register",
    "KlassenChartaGeltung", "KlassenChartaNorm", "KlassenChartaProzedur", "KlassenChartaTyp",
    "KlassenCharta", "build_klassen_charta",
    "StrukturKodexGeltung", "StrukturKodexNorm", "StrukturKodexProzedur", "StrukturKodexTyp",
    "StrukturKodex", "build_struktur_kodex",
    "HabitusManifestGeltung", "HabitusManifestNorm", "HabitusManifestProzedur", "HabitusManifestTyp",
    "HabitusManifest", "build_habitus_manifest",
    "StrukturierungsPaktGeltung", "StrukturierungsPaktNorm", "StrukturierungsPaktProzedur", "StrukturierungsPaktTyp",
    "StrukturierungsPakt", "build_strukturierungs_pakt",
    "KommunikationsSenatGeltung", "KommunikationsSenatNorm", "KommunikationsSenatProzedur", "KommunikationsSenatTyp",
    "KommunikationsSenat", "build_kommunikations_senat",
    "SoziologieNormGeltung", "SoziologieNormEintrag", "SoziologieNormProzedur", "SoziologieNormTyp",
    "SoziologieNormSatz", "build_soziologie_norm",
    "NetzwerkgesellschaftsChartaGeltung", "NetzwerkgesellschaftsChartaNorm", "NetzwerkgesellschaftsChartaProzedur", "NetzwerkgesellschaftsChartaTyp",
    "NetzwerkgesellschaftsCharta", "build_netzwerkgesellschafts_charta",
    "SoziologieVerfassungsGeltung", "SoziologieVerfassungsNorm", "SoziologieVerfassungsProzedur", "SoziologieVerfassungsTyp",
    "SoziologieVerfassung", "build_soziologie_verfassung",
    # Block #501–#510: Ethik & Moralphilosophie
    "EthikFeldGeltung", "EthikFeldNorm", "EthikFeldProzedur", "EthikFeldTyp",
    "EthikFeld", "build_ethik_feld",
    "UtilitarismusRegisterGeltung", "UtilitarismusRegisterNorm", "UtilitarismusRegisterProzedur", "UtilitarismusRegisterTyp",
    "UtilitarismusRegister", "build_utilitarismus_register",
    "GerechtigkeitsChartaGeltung", "GerechtigkeitsChartaNorm", "GerechtigkeitsChartaProzedur", "GerechtigkeitsChartaTyp",
    "GerechtigkeitsCharta", "build_gerechtigkeits_charta",
    "TugendKodexGeltung", "TugendKodexNorm", "TugendKodexProzedur", "TugendKodexTyp",
    "TugendKodex", "build_tugend_kodex",
    "DiskursManifestGeltung", "DiskursManifestNorm", "DiskursManifestProzedur", "DiskursManifestTyp",
    "DiskursManifest", "build_diskurs_manifest",
    "FuersorgeEthikPaktGeltung", "FuersorgeEthikPaktNorm", "FuersorgeEthikPaktProzedur", "FuersorgeEthikPaktTyp",
    "FuersorgeEthikPakt", "build_fuersorge_ethik_pakt",
    "MetaEthikSenatGeltung", "MetaEthikSenatNorm", "MetaEthikSenatProzedur", "MetaEthikSenatTyp",
    "MetaEthikSenat", "build_meta_ethik_senat",
    "EthikNormGeltung", "EthikNormEintrag", "EthikNormProzedur", "EthikNormTyp",
    "EthikNormSatz", "build_ethik_norm",
    "AngewandteEthikChartaGeltung", "AngewandteEthikChartaNorm", "AngewandteEthikChartaProzedur", "AngewandteEthikChartaTyp",
    "AngewandteEthikCharta", "build_angewandte_ethik_charta",
    "EthikVerfassungsGeltung", "EthikVerfassungsNorm", "EthikVerfassungsProzedur", "EthikVerfassungsTyp",
    "EthikVerfassung", "build_ethik_verfassung",
    "PolitikFeldGeltung", "PolitikFeldNorm", "PolitikFeldProzedur", "PolitikFeldTyp",
    "PolitikFeld", "build_politik_feld",
    "StaatstheorieRegisterGeltung", "StaatstheorieRegisterNorm", "StaatstheorieRegisterProzedur", "StaatstheorieRegisterTyp",
    "StaatstheorieRegister", "build_staatstheorie_register",
    "DemokratieChartaGeltung", "DemokratieChartaNorm", "DemokratieChartaProzedur", "DemokratieChartaTyp",
    "DemokratieCharta", "build_demokratie_charta",
    "MachtKodexGeltung", "MachtKodexNorm", "MachtKodexProzedur", "MachtKodexTyp",
    "MachtKodex", "build_macht_kodex",
    "GewaltenteilungsManifestGeltung", "GewaltenteilungsManifestNorm", "GewaltenteilungsManifestProzedur", "GewaltenteilungsManifestTyp",
    "GewaltenteilungsManifest", "build_gewaltenteilungs_manifest",
    "LegitimitaetsPaktGeltung", "LegitimitaetsPaktNorm", "LegitimitaetsPaktProzedur", "LegitimitaetsPaktTyp",
    "LegitimitaetsPakt", "build_legitimitaets_pakt",
    "GlobalpolitikSenatGeltung", "GlobalpolitikSenatNorm", "GlobalpolitikSenatProzedur", "GlobalpolitikSenatTyp",
    "GlobalpolitikSenat", "build_globalpolitik_senat",
    "PolitikNormGeltung", "PolitikNormEintrag", "PolitikNormProzedur", "PolitikNormTyp",
    "PolitikNormSatz", "build_politik_norm",
    "ZivilgesellschaftsChartaGeltung", "ZivilgesellschaftsChartaNorm", "ZivilgesellschaftsChartaProzedur", "ZivilgesellschaftsChartaTyp",
    "ZivilgesellschaftsCharta", "build_zivilgesellschafts_charta",
    "PolitikVerfassungsGeltung", "PolitikVerfassungsNorm", "PolitikVerfassungsProzedur", "PolitikVerfassungsTyp",
    "PolitikVerfassung", "build_politik_verfassung",
    "WirtschaftsFeldGeltung", "WirtschaftsFeldNorm", "WirtschaftsFeldProzedur", "WirtschaftsFeldTyp",
    "WirtschaftsFeld", "build_wirtschafts_feld",
    "MarktRegisterGeltung", "MarktRegisterNorm", "MarktRegisterProzedur", "MarktRegisterTyp",
    "MarktRegister", "build_markt_register",
    "KapitalChartaGeltung", "KapitalChartaNorm", "KapitalChartaProzedur", "KapitalChartaTyp",
    "KapitalCharta", "build_kapital_charta",
    "KonjunkturKodexGeltung", "KonjunkturKodexNorm", "KonjunkturKodexProzedur", "KonjunkturKodexTyp",
    "KonjunkturKodex", "build_konjunktur_kodex",
    "WirtschaftsOrdnungsManifestGeltung", "WirtschaftsOrdnungsManifestNorm", "WirtschaftsOrdnungsManifestProzedur", "WirtschaftsOrdnungsManifestTyp",
    "WirtschaftsOrdnungsManifest", "build_ordnungs_manifest",
    "InnovationsPaktGeltung", "InnovationsPaktNorm", "InnovationsPaktProzedur", "InnovationsPaktTyp",
    "InnovationsPakt", "build_innovations_pakt",
    "WohlfahrtsSenatGeltung", "WohlfahrtsSenatNorm", "WohlfahrtsSenatProzedur", "WohlfahrtsSenatTyp",
    "WohlfahrtsSenat", "build_wohlfahrts_senat",
    "WirtschaftsNormGeltung", "WirtschaftsNormEintrag", "WirtschaftsNormProzedur", "WirtschaftsNormTyp",
    "WirtschaftsNormSatz", "build_wirtschafts_norm",
    "InstitutionenChartaGeltung", "InstitutionenChartaNorm", "InstitutionenChartaProzedur", "InstitutionenChartaTyp",
    "InstitutionenCharta", "build_institutionen_charta",
    "WirtschaftsVerfassungsGeltung", "WirtschaftsVerfassungsNorm", "WirtschaftsVerfassungsProzedur", "WirtschaftsVerfassungsTyp",
    "WirtschaftsVerfassung", "build_wirtschafts_verfassung",
    "RechtsFeldGeltung", "RechtsFeldNorm", "RechtsFeldProzedur", "RechtsFeldTyp",
    "RechtsFeld", "build_rechts_feld",
    "RechtssystemRegisterGeltung", "RechtssystemRegisterNorm", "RechtssystemRegisterProzedur", "RechtssystemRegisterTyp",
    "RechtssystemRegister", "build_rechts_system_register",
    "VerfassungsrechtsChartaGeltung", "VerfassungsrechtsChartaNorm", "VerfassungsrechtsChartaProzedur", "VerfassungsrechtsChartaTyp",
    "VerfassungsrechtsCharta", "build_verfassungsrechts_charta",
    "VoelkerrechtsKodexGeltung", "VoelkerrechtsKodexNorm", "VoelkerrechtsKodexProzedur", "VoelkerrechtsKodexTyp",
    "VoelkerrechtsKodexJurisprudenz", "build_voelkerrechts_kodex_jurisprudenz",
    "RechtsphilosophieManifestGeltung", "RechtsphilosophieManifestNorm", "RechtsphilosophieManifestProzedur", "RechtsphilosophieManifestTyp",
    "RechtsphilosophieManifest", "build_rechtsphilosophie_manifest",
    "RechtssoziologiePaktGeltung", "RechtssoziologiePaktNorm", "RechtssoziologiePaktProzedur", "RechtssoziologiePaktTyp",
    "RechtssoziologiePakt", "build_rechtssoziologie_pakt",
    "StrafrechtsSenatGeltung", "StrafrechtsSenatNorm", "StrafrechtsSenatProzedur", "StrafrechtsSenatTyp",
    "StrafrechtsSenat", "build_strafrechts_senat",
    "RechtsNormGeltung", "RechtsNormEintrag", "RechtsNormProzedur", "RechtsNormTyp",
    "RechtsNormSatz", "build_rechts_norm",
    "ZivilrechtsChartaGeltung", "ZivilrechtsChartaNorm", "ZivilrechtsChartaProzedur", "ZivilrechtsChartaTyp",
    "ZivilrechtsCharta", "build_zivilrechts_charta",
    "RechtsVerfassungsGeltung", "RechtsVerfassungsNorm", "RechtsVerfassungsProzedur", "RechtsVerfassungsTyp",
    "RechtsVerfassung", "build_rechts_verfassung",
    # --- Block #35: Geschichtswissenschaft & Historiographie (#541–#550) ---
    "GeschichtsFeldGeltung", "GeschichtsFeldNorm", "GeschichtsFeldProzedur", "GeschichtsFeldTyp",
    "GeschichtsFeld", "build_geschichts_feld",
    "HistoriographieRegisterGeltung", "HistoriographieRegisterNorm", "HistoriographieRegisterProzedur", "HistoriographieRegisterTyp",
    "HistoriographieRegister", "build_historiographie_register",
    "QuellenChartaGeltung", "QuellenChartaNorm", "QuellenChartaProzedur", "QuellenChartaTyp",
    "QuellenCharta", "build_quellen_charta",
    "EpochenKodexGeltung", "EpochenKodexNorm", "EpochenKodexProzedur", "EpochenKodexTyp",
    "EpochenKodex", "build_epochen_kodex",
    "AnnalesManifestGeltung", "AnnalesManifestNorm", "AnnalesManifestProzedur", "AnnalesManifestTyp",
    "AnnalesManifest", "build_annales_manifest",
    "ZeitgeschichtsPaktGeltung", "ZeitgeschichtsPaktNorm", "ZeitgeschichtsPaktProzedur", "ZeitgeschichtsPaktTyp",
    "ZeitgeschichtsPakt", "build_zeitgeschichts_pakt",
    "GeschichtsSenatGeltung", "GeschichtsSenatNorm", "GeschichtsSenatProzedur", "GeschichtsSenatTyp",
    "GeschichtsSenat", "build_geschichts_senat",
    "GeschichtsNormGeltung", "GeschichtsNormEintrag", "GeschichtsNormProzedur", "GeschichtsNormTyp",
    "GeschichtsNormSatz", "build_geschichts_norm",
    "HistoriographieChartaGeltung", "HistoriographieChartaNorm", "HistoriographieChartaProzedur", "HistoriographieChartaTyp",
    "HistoriographieCharta", "build_historiographie_charta",
    "GeschichtsVerfassungsGeltung", "GeschichtsVerfassungsNorm", "GeschichtsVerfassungsProzedur", "GeschichtsVerfassungsTyp",
    "GeschichtsVerfassung", "build_geschichts_verfassung",
    "KulturFeldGeltung", "KulturFeldNorm", "KulturFeldProzedur", "KulturFeldTyp",
    "KulturFeld", "build_kultur_feld",
    "KulturanthropologieRegisterGeltung", "KulturanthropologieRegisterNorm", "KulturanthropologieRegisterProzedur", "KulturanthropologieRegisterTyp",
    "KulturanthropologieRegister", "build_kulturanthropologie_register",
    "EthnographieChartaGeltung", "EthnographieChartaNorm", "EthnographieChartaProzedur", "EthnographieChartaTyp",
    "EthnographieCharta", "build_ethnographie_charta",
    "RitualKodexGeltung", "RitualKodexNorm", "RitualKodexProzedur", "RitualKodexTyp",
    "RitualKodex", "build_ritual_kodex",
    "KultursystemeManifestGeltung", "KultursystemeManifestNorm", "KultursystemeManifestProzedur", "KultursystemeManifestTyp",
    "KultursystemeManifest", "build_kultursysteme_manifest",
    "KulturgedaechnisPaktGeltung", "KulturgedaechnisPaktNorm", "KulturgedaechnisPaktProzedur", "KulturgedaechnisPaktTyp",
    "KulturgedaechnisPakt", "build_kulturgedaechtnis_pakt",
    "KultursoziologieSenatGeltung", "KultursoziologieSenatNorm", "KultursoziologieSenatProzedur", "KultursoziologieSenatTyp",
    "KultursoziologieSenat", "build_kultursoziologie_senat",
    "KulturNormTyp", "KulturNormProzedur", "KulturNormGeltung", "KulturNormEintrag", "KulturNormSatz", "build_kultur_norm",
    "KulturelleIdentitaetsChartaGeltung", "KulturelleIdentitaetsChartaNorm", "KulturelleIdentitaetsChartaProzedur", "KulturelleIdentitaetsChartaTyp",
    "KulturelleIdentitaetsCharta", "build_kulturelle_identitaets_charta",
    "KulturVerfassungsGeltung", "KulturVerfassungsNorm", "KulturVerfassungsProzedur", "KulturVerfassungsTyp",
    "KulturVerfassung", "build_kultur_verfassung",
    "MedienFeldGeltung", "MedienFeldNorm", "MedienFeldProzedur", "MedienFeldTyp",
    "MedienFeld", "build_medien_feld",
    "KommunikationsRegisterGeltung", "KommunikationsRegisterNorm", "KommunikationsRegisterProzedur", "KommunikationsRegisterTyp",
    "KommunikationsRegister", "build_kommunikations_register",
    "MedientheorieChartaGeltung", "MedientheorieChartaNorm", "MedientheorieChartaProzedur", "MedientheorieChartaTyp",
    "MedientheorieCharta", "build_medientheorie_charta",
    "InformationsKodexGeltung", "InformationsKodexNorm", "InformationsKodexProzedur", "InformationsKodexTyp",
    "InformationsKodex", "build_informations_kodex",
    "MedienDiskursManifestGeltung", "MedienDiskursManifestNorm", "MedienDiskursManifestProzedur", "MedienDiskursManifestTyp",
    "MedienDiskursManifest", "build_medien_diskurs_manifest",
    "OeffentlichkeitsPaktGeltung", "OeffentlichkeitsPaktNorm", "OeffentlichkeitsPaktProzedur", "OeffentlichkeitsPaktTyp",
    "OeffentlichkeitsPakt", "build_oeffentlichkeits_pakt",
    "MedienSenatGeltung", "MedienSenatNorm", "MedienSenatProzedur", "MedienSenatTyp",
    "MedienSenat", "build_medien_senat",
    "MedienNormTyp", "MedienNormProzedur", "MedienNormGeltung", "MedienNormEintrag", "MedienNormSatz", "build_medien_norm",
    "KommunikativeHandlungsChartaGeltung", "KommunikativeHandlungsChartaNorm", "KommunikativeHandlungsChartaProzedur", "KommunikativeHandlungsChartaTyp",
    "KommunikativeHandlungsCharta", "build_kommunikative_handlungs_charta",
    "MedienVerfassungsGeltung", "MedienVerfassungsNorm", "MedienVerfassungsProzedur", "MedienVerfassungsTyp",
    "MedienVerfassung", "build_medien_verfassung",
    "KunstFeldGeltung", "KunstFeldNorm", "KunstFeldProzedur", "KunstFeldTyp",
    "KunstFeld", "build_kunst_feld",
    "AesthetikRegisterGeltung", "AesthetikRegisterNorm", "AesthetikRegisterProzedur", "AesthetikRegisterTyp",
    "AesthetikRegister", "build_aesthetik_register",
    "KunsttheorieChartaGeltung", "KunsttheorieChartaNorm", "KunsttheorieChartaProzedur", "KunsttheorieChartaTyp",
    "KunsttheorieCharta", "build_kunsttheorie_charta",
    "StilkritikKodexGeltung", "StilkritikKodexNorm", "StilkritikKodexProzedur", "StilkritikKodexTyp",
    "StilkritikKodex", "build_stilkritik_kodex",
    "KunstgeschichteManifestGeltung", "KunstgeschichteManifestNorm", "KunstgeschichteManifestProzedur", "KunstgeschichteManifestTyp",
    "KunstgeschichteManifest", "build_kunstgeschichte_manifest",
    "IkonographiePaktGeltung", "IkonographiePaktNorm", "IkonographiePaktProzedur", "IkonographiePaktTyp",
    "IkonographiePakt", "build_ikonographie_pakt",
    "KunstsoziologieSenatGeltung", "KunstsoziologieSenatNorm", "KunstsoziologieSenatProzedur", "KunstsoziologieSenatTyp",
    "KunstsoziologieSenat", "build_kunstsoziologie_senat",
    "KunstNormTyp", "KunstNormProzedur", "KunstNormGeltung", "KunstNormEintrag", "KunstNormSatz", "build_kunst_norm",
    "AesthetischeUrteilsChartaGeltung", "AesthetischeUrteilsChartaNorm", "AesthetischeUrteilsChartaProzedur", "AesthetischeUrteilsChartaTyp",
    "AesthetischeUrteilsCharta", "build_aesthetische_urteils_charta",
    "KunstVerfassungsGeltung", "KunstVerfassungsNorm", "KunstVerfassungsProzedur", "KunstVerfassungsTyp",
    "KunstVerfassung", "build_kunst_verfassung",
    "PaedagogikFeldGeltung", "PaedagogikFeldNorm", "PaedagogikFeldProzedur", "PaedagogikFeldTyp",
    "PaedagogikFeld", "build_paedagogik_feld",
    "BildungstheorieRegisterGeltung", "BildungstheorieRegisterNorm", "BildungstheorieRegisterProzedur", "BildungstheorieRegisterTyp",
    "BildungstheorieRegister", "build_bildungstheorie_register",
    "LerntheorieChartaGeltung", "LerntheorieChartaNorm", "LerntheorieChartaProzedur", "LerntheorieChartaTyp",
    "LerntheorieCharta", "build_lerntheorie_charta",
    "DidaktikKodexGeltung", "DidaktikKodexNorm", "DidaktikKodexProzedur", "DidaktikKodexTyp",
    "DidaktikKodex", "build_didaktik_kodex",
    "CurriculumManifestGeltung", "CurriculumManifestNorm", "CurriculumManifestProzedur", "CurriculumManifestTyp",
    "CurriculumManifest", "build_curriculum_manifest",
    "BildungsinstitutionPaktGeltung", "BildungsinstitutionPaktNorm", "BildungsinstitutionPaktProzedur", "BildungsinstitutionPaktTyp",
    "BildungsinstitutionPakt", "build_bildungsinstitution_pakt",
    "PaedagogikSenatGeltung", "PaedagogikSenatNorm", "PaedagogikSenatProzedur", "PaedagogikSenatTyp",
    "PaedagogikSenat", "build_paedagogik_senat",
    "PaedagogikNormTyp", "PaedagogikNormProzedur", "PaedagogikNormGeltung", "PaedagogikNormEintrag", "PaedagogikNormSatz", "build_paedagogik_norm",
    "BildungsphilosophieChartaGeltung", "BildungsphilosophieChartaNorm", "BildungsphilosophieChartaProzedur", "BildungsphilosophieChartaTyp",
    "BildungsphilosophieCharta", "build_bildungsphilosophie_charta",
    "PaedagogikVerfassungsGeltung", "PaedagogikVerfassungsNorm", "PaedagogikVerfassungsProzedur", "PaedagogikVerfassungsTyp",
    "PaedagogikVerfassung", "build_paedagogik_verfassung",
    "PsychologieFeldGeltung", "PsychologieFeldNorm", "PsychologieFeldProzedur", "PsychologieFeldTyp",
    "PsychologieFeld", "build_psychologie_feld",
    "KognitionswissenschaftRegisterGeltung", "KognitionswissenschaftRegisterNorm", "KognitionswissenschaftRegisterProzedur", "KognitionswissenschaftRegisterTyp",
    "KognitionswissenschaftRegister", "build_kognitionswissenschaft_register",
    "BewusstseinsChartaGeltung", "BewusstseinsChartaNorm", "BewusstseinsChartaProzedur", "BewusstseinsChartaTyp",
    "BewusstseinsCharta", "build_bewusstseins_charta",
    "VerhaltensKodexGeltung", "VerhaltensKodexNorm", "VerhaltensKodexProzedur", "VerhaltensKodexTyp",
    "VerhaltensKodex", "build_verhaltens_kodex",
    "EntwicklungsManifestGeltung", "EntwicklungsManifestNorm", "EntwicklungsManifestProzedur", "EntwicklungsManifestTyp",
    "EntwicklungsManifest", "build_entwicklungs_manifest",
    "SozialpsychologiePaktGeltung", "SozialpsychologiePaktNorm", "SozialpsychologiePaktProzedur", "SozialpsychologiePaktTyp",
    "SozialpsychologiePakt", "build_sozialpsychologie_pakt",
    "PsychologieSenatGeltung", "PsychologieSenatNorm", "PsychologieSenatProzedur", "PsychologieSenatTyp",
    "PsychologieSenat", "build_psychologie_senat",
    "PsychologieNormTyp", "PsychologieNormProzedur", "PsychologieNormGeltung", "PsychologieNormEintrag", "PsychologieNormSatz", "build_psychologie_norm",
    "KognitionsChartaGeltung", "KognitionsChartaNorm", "KognitionsChartaProzedur", "KognitionsChartaTyp",
    "KognitionsCharta", "build_kognitions_charta",
    "PsychologieVerfassungsGeltung", "PsychologieVerfassungsNorm", "PsychologieVerfassungsProzedur", "PsychologieVerfassungsTyp",
    "PsychologieVerfassung", "build_psychologie_verfassung",
    "LinguistikFeldGeltung", "LinguistikFeldNorm", "LinguistikFeldProzedur", "LinguistikFeldTyp",
    "LinguistikFeld", "build_linguistik_feld",
    "SprachphonikRegisterGeltung", "SprachphonikRegisterNorm", "SprachphonikRegisterTyp",
    "SprachphonikRegister", "build_sprachphonik_register",
    "MorphologieChartaGeltung", "MorphologieChartaNorm", "MorphologieChartaProzedur", "MorphologieChartaTyp",
    "MorphologieCharta", "build_morphologie_charta",
    "SyntaxKodexGeltung", "SyntaxKodexNorm", "SyntaxKodexProzedur", "SyntaxKodexTyp",
    "SyntaxKodex", "build_syntax_kodex",
    "SemantikManifestGeltung", "SemantikManifestNorm", "SemantikManifestProzedur", "SemantikManifestTyp",
    "SemantikManifest", "build_semantik_manifest",
    "DiskursPaktGeltung", "DiskursPaktNorm", "DiskursPaktTyp",
    "DiskursPakt", "build_diskurs_pakt",
    "LinguistikSenatGeltung", "LinguistikSenatNorm", "LinguistikSenatProzedur", "LinguistikSenatTyp",
    "LinguistikSenat", "build_linguistik_senat",
    "LinguistikNormTyp", "LinguistikNormProzedur", "LinguistikNormGeltung", "LinguistikNormEintrag", "LinguistikNormSatz", "build_linguistik_norm",
    "SemiotikChartaGeltung", "SemiotikChartaNorm", "SemiotikChartaProzedur", "SemiotikChartaTyp",
    "SemiotikCharta", "build_semiotik_charta",
    "SprachwissenschaftVerfassungGeltung", "SprachwissenschaftVerfassungsNorm", "SprachwissenschaftVerfassungProzedur", "SprachwissenschaftVerfassungTyp",
    "SprachwissenschaftVerfassung", "build_sprachwissenschaft_verfassung",
    "ReligionsFeldGeltung", "ReligionsFeldNorm", "ReligionsFeldProzedur", "ReligionsFeldTyp",
    "ReligionsFeld", "build_religions_feld",
    "MythosRegisterGeltung", "MythosRegisterNorm", "MythosRegisterTyp",
    "MythosRegister", "build_mythos_register",
    "HeiligeTraditionChartaGeltung", "HeiligeTraditionChartaNorm", "HeiligeTraditionChartaTyp",
    "HeiligeTraditionCharta", "build_heilige_tradition_charta",
    "TheologieKodexGeltung", "TheologieKodexNorm", "TheologieKodexTyp",
    "TheologieKodex", "build_theologie_kodex",
    "GlaubensManifestGeltung", "GlaubensManifestNorm", "GlaubensManifestTyp",
    "GlaubensManifest", "build_glaubens_manifest",
    "SpiritualitaetsPaktGeltung", "SpiritualitaetsPaktNorm", "SpiritualitaetsPaktTyp",
    "SpiritualitaetsPakt", "build_spiritualitaets_pakt",
    "ReligionsphilosophieSenatGeltung", "ReligionsphilosophieSenatNorm", "ReligionsphilosophieSenatTyp",
    "ReligionsphilosophieSenat", "build_religionsphilosophie_senat",
    "ReligionsNormTyp", "ReligionsNormProzedur", "ReligionsNormGeltung", "ReligionsNormEintrag", "ReligionsNormSatz", "build_religions_norm",
    "SakraleChartaGeltung", "SakraleChartaNorm", "SakraleChartaProzedur", "SakraleChartaTyp",
    "SakraleCharta", "build_sakrale_charta",
    "ReligionswissenschaftVerfassungGeltung", "ReligionswissenschaftVerfassungsNorm", "ReligionswissenschaftVerfassungProzedur", "ReligionswissenschaftVerfassungTyp",
    "ReligionswissenschaftVerfassung", "build_religionswissenschaft_verfassung",
]
