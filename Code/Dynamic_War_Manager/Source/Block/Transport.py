from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from Code.Dynamic_War_Manager.Source.Block.Block import Block
from Code.Dynamic_War_Manager.Source.Utility.Utility import setName
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from Code.Dynamic_War_Manager.Source.Context.Context import validate_infrastructure_sub_category

if TYPE_CHECKING:
    from Code.Dynamic_War_Manager.Source.Context.Region import Region


# LOGGING --
logger = Logger(module_name = __name__, class_name = 'Transport').logger


# BLOCK
class Transport(Block):
    """Blocco infrastrutturale di trasporto (strade, ferrovie, porti, aeroporti, eliporti, linee elettriche e di carburante).

    Blocco NON militare: non ha mil_category, combat power ne' capacita' di intercettazione,
    e nel motore di sessioni virtuali non puo' disingaggiarsi (v. Logic/Engagement_Resolver,
    soglie di disingaggio). Le sotto-categorie ammesse sono le chiavi di
    Context.BLOCK_INFRASTRUCTURE_ASSET['Transport'].
    """

    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        side: Optional[str] = None,
        category: Optional[str] = None,
        sub_category: Optional[str] = None,
        functionality: Optional[str] = None,
        value: Optional[int] = None,
        region: Optional["Region"] = None,
        id: Optional[str] = None
    ) -> None:
        """
        Initialize a Transport instance.

        Firma allineata a Block.__init__ (keyword arguments, stesso pattern di Military): il
        vecchio costruttore passava argomenti posizionali non corrispondenti (acp/rcp/payload,
        concetti mai esistiti su Block) e chiamava un checkParam inesistente, quindi la classe
        non era mai istanziabile.

        Args:
            name: Base name (prefissato con 'Transport.'; se assente 'Unnamed_Transport_#nnnn')
            description: Base description
            side: Base side (Blue/Red/Neutral)
            category: Base category (es. 'Logistic', 'Civilian')
            sub_category: sotto-categoria infrastrutturale, validata contro
                          Context.BLOCK_INFRASTRUCTURE_ASSET['Transport'] se fornita
            functionality: Base functionality
            value: Strategic value
            region: Associated region
            id: id di dominio esplicito, stabile fra le esecuzioni (v. Block.__init__)

        Raises:
            ValueError: sub_category fornita ma non ammessa per Transport (oltre alle
                        validazioni di Block.__init__).
        """
        super().__init__(
            name=f"Transport.{name}" if name else setName('Unnamed_Transport'),
            description=description,
            side=side,
            category=category,
            sub_category=sub_category,
            functionality=functionality,
            value=value,
            region=region,
            id=id
        )

        validate_infrastructure_sub_category('Transport', sub_category)
