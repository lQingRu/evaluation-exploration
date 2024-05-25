from pydantic import BaseModel


class Prompt(BaseModel):
    id: int
    system_prompt: str
    user_prompt: str

    def get_concatenated_prompt(self) -> str:
        return f"""
        {self.system_prompt}

        {self.user_prompt}
        """
