from app.models.refresh_token import RefreshToken


class TokenRepository:

    @staticmethod
    def create(db, token_obj):
        db.add(token_obj)
        db.commit()
        db.refresh(token_obj)
        return token_obj

    @staticmethod
    def get_by_token(db, token: str):
        return (
            db.query(RefreshToken)
            .filter(RefreshToken.token == token)
            .first()
        )

    @staticmethod
    def revoke(db, token_record):
        token_record.revoked = True
        db.commit()