import streamlit as st
import random
import string
from datetime import datetime

# --------- CONFIG DE LA PAGE ---------
st.set_page_config(
    page_title="ZeyPay - Crypto Gift Cards",
    page_icon="🎁",
    layout="centered",
)

st.title("🎁 ZeyPay – Crypto Gift Cards (Prototype)")
st.caption("Fintech & DeFi – Streamlit prototype demo")


# --------- INIT "BASE DE DONNÉES" EN MÉMOIRE ---------
if "gift_cards" not in st.session_state:
    # gift_cards: dict[code] = {...}
    st.session_state.gift_cards = {}


# --------- FONCTIONS UTILITAIRES ---------
def generate_card_code(length: int = 8) -> str:
    """Génère un code de carte cadeau pseudo-aléatoire."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choices(alphabet, k=length))


def get_fake_crypto_rates():
    """
    Taux simulés pour la démo.
    On suppose des prix en USD.
    """
    return {
        "BTC": 60000,   # 1 BTC = 60 000 USD
        "ETH": 3000,    # 1 ETH = 3 000 USD
        "USDC": 1,      # 1 USDC = 1 USD (stablecoin)
    }


def fiat_to_usd(amount: float, fiat: str) -> float:
    """Conversion simplifiée en USD (pour la démo)."""
    rates = {
        "EUR": 1.1,   # 1 EUR = 1.1 USD
        "USD": 1.0,   # 1 USD = 1 USD
        "GBP": 1.25,  # 1 GBP = 1.25 USD
    }
    return amount * rates.get(fiat, 1.0)


# --------- NAVIGATION ---------
tab_create, tab_redeem, tab_admin = st.tabs(
    ["✨ Create Gift Card", "🔓 Redeem Gift Card", "📊 Demo / Admin view"]
)


# --------- ONGLET 1 : CRÉATION DE GIFT CARD ---------
with tab_create:
    st.subheader("Create a crypto gift card")

    col1, col2 = st.columns(2)
    with col1:
        fiat_currency = st.selectbox("Fiat currency", ["EUR", "USD", "GBP"])
    with col2:
        amount_fiat = st.number_input(
            "Amount",
            min_value=5.0,
            max_value=10000.0,
            value=50.0,
            step=5.0,
        )

    recipient_name = st.text_input("Recipient name (optional)")
    personal_message = st.text_area("Personal message")

    st.markdown(
        "_Your gift card will be held in a simulated blockchain escrow until redemption._"
    )

    if st.button("Generate gift card 🚀"):
        if amount_fiat <= 0:
            st.error("Please enter a positive amount.")
        else:
            code = generate_card_code()
            created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"

            # Enregistrer dans la "base" en mémoire
            st.session_state.gift_cards[code] = {
                "fiat_currency": fiat_currency,
                "amount_fiat": amount_fiat,
                "recipient_name": recipient_name,
                "message": personal_message,
                "status": "pending",  # pending / redeemed
                "created_at": created_at,
                "redeemed_at": None,
                "redeemed_crypto": None,
                "redeemed_amount_crypto": None,
            }

            gift_url = f"https://zeypay.com/card/{code}"

            st.success("Gift card successfully created! 🎉")
            st.write("Share this code or link with the recipient:")

            st.code(code, language="text")
            st.markdown(f"🔗 **Gift link:** {gift_url}")

            with st.expander("Preview of what the recipient sees"):
                st.markdown(
                    f"""
                    **You received a crypto gift card from {recipient_name or "a friend"}!**  

                    - Amount: **{amount_fiat:.2f} {fiat_currency}**  
                    - Message: _{personal_message or "(no message)"}_  
                    - Card code: `{code}`  
                    """
                )


# --------- ONGLET 2 : RÉDEMPTION ---------
with tab_redeem:
    st.subheader("Redeem a gift card")

    st.markdown("Paste the **gift card code** you received:")

    input_code = st.text_input("Gift card code")

    if input_code:
        code = input_code.strip().upper()
        card = st.session_state.gift_cards.get(code)

        if card is None:
            st.error("❌ Gift card not found. Check the code.")
        else:
            st.markdown(
                f"""
                **Gift card details**  

                - Status: `{card['status']}`  
                - Original amount: **{card['amount_fiat']:.2f} {card['fiat_currency']}**  
                - From: {card['recipient_name'] or "Unknown"}  
                - Message: _{card['message'] or "(no message)"}_  
                """
            )

            if card["status"] == "redeemed":
                st.warning(
                    f"⚠️ This card was already redeemed on {card['redeemed_at']} "
                    f"in **{card['redeemed_crypto']}** "
                    f"({card['redeemed_amount_crypto']:.6f} {card['redeemed_crypto']})."
                )
            else:
                st.markdown("### Choose the cryptocurrency to redeem:")

                crypto_choice = st.selectbox("Crypto", ["BTC", "ETH", "USDC"])
                rates = get_fake_crypto_rates()

                amount_usd = fiat_to_usd(card["amount_fiat"], card["fiat_currency"])
                crypto_price_usd = rates[crypto_choice]
                amount_crypto = amount_usd / crypto_price_usd

                st.info(
                    f"""
                    💱 **Simulated conversion**

                    - Fiat amount (approx in USD): **{amount_usd:.2f} USD**  
                    - {crypto_choice} price (simulated): **{crypto_price_usd:,.0f} USD**  
                    - You would receive: **{amount_crypto:.6f} {crypto_choice}**  
                    """
                )

                st.markdown(
                    "_In a real app, this would call a DEX / on-chain smart contract and send funds to the user's wallet._"
                )

                wallet_address = st.text_input(
                    "Recipient wallet address (simulated)", placeholder="0x1234... or BTC address"
                )

                if st.button("Confirm redemption ✅"):
                    if not wallet_address:
                        st.error("Please enter a (simulated) wallet address.")
                    else:
                        # Update card status
                        card["status"] = "redeemed"
                        card["redeemed_at"] = datetime.utcnow().isoformat(
                            timespec="seconds"
                        ) + "Z"
                        card["redeemed_crypto"] = crypto_choice
                        card["redeemed_amount_crypto"] = amount_crypto

                        st.session_state.gift_cards[code] = card

                        st.success("Gift card redeemed successfully! 🎉")
                        st.markdown(
                            f"You received **{amount_crypto:.6f} {crypto_choice}** "
                            f"to wallet `{wallet_address}` (simulated)."
                        )


# --------- ONGLET 3 : VUE "ADMIN / DEMO" ---------
with tab_admin:
    st.subheader("Demo / Admin view (for the pitch)")

    st.caption(
        "This tab is only to help you show what's stored server-side "
        "when you generate and redeem gift cards."
    )

    if not st.session_state.gift_cards:
        st.info("No gift cards created yet in this session.")
    else:
        st.write("Current in-memory gift cards:")
        st.json(st.session_state.gift_cards)