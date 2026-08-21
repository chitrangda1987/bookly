from pydantic import BaseModel


class PublicUser(BaseModel):
    name: str
    email: str


class StoredUser(BaseModel):
    name: str
    email: str
    password_hash: str

    def public(self) -> PublicUser:
        return PublicUser(name=self.name, email=self.email)
