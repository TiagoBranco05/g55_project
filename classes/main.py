from airline    import Airline
from promotion  import Promotion
from reward     import Reward
from redemption import Redemption

def main():
    caminho_bd = 'G55.db'

    stats = Airline.load_db(caminho_bd)

    print("\nResumo dos dados carregados:")
    print(f"- Companhias aéreas: {stats['airlines']}")
    print(f"- Promoções:         {stats['promotions']}")
    print(f"- Recompensas:       {stats['rewards']}")
    print(f"- Resgates:          {stats['redemptions']}")

    print("\nLeitura individual:")

    if len(Airline.lst) > 0:
        primeira = Airline.obj[Airline.lst[0]]
        print(f"- A primeira companhia aérea é: {primeira.name}")
        print(f"  Fundada em: {primeira.created_date}")

    if len(Promotion.lst) > 0:
        id_promo    = Promotion.lst[0]
        primeira_promo = Promotion.obj[id_promo]
        print(f"- A primeira promoção chama-se: {primeira_promo.name}")
        print(f"  Mínimo de milhas exigido: {primeira_promo.min_miles}")

    if len(Reward.lst) > 0:
        id_reward    = Reward.lst[0]
        primeira_reward = Reward.obj[id_reward]
        print(f"- A primeira recompensa é: {primeira_reward.name}")
        print(f"  Validade: {primeira_reward.expiry_days} dias")

    if len(Redemption.lst) > 0:
        id_red     = Redemption.lst[0]
        primeiro_red = Redemption.obj[id_red]
        print(f"- O primeiro resgate foi feito pelo passageiro: {primeiro_red.passenger_id}")
        print(f"  Milhas usadas: {primeiro_red.miles_used}")

    print("\nRelações entre classes:")

    if len(Airline.lst) > 0:
        companhia = Airline.obj[Airline.lst[0]]
        promos    = companhia.get_promotions()
        print(f"- A companhia '{companhia.name}' tem {len(promos)} promoção(ões) associada(s)")

    if len(Promotion.lst) > 0:
        promo   = Promotion.obj[Promotion.lst[0]]
        reward  = promo.get_reward()
        if reward:
            print(f"- A promoção '{promo.name}' dá como recompensa: {reward.name}")

if __name__ == "__main__":
    main()
