from discord.ext import commands 

class Genre(commands.Converter):
    async def convert(
        self, 
        ctx, 
        argument: str
    ):
        genres = [
            'male',
            'female',
            'anime'
        ]
        if not argument.lower() in genres: 
            raise commands.BadArgument("Genres can be: male, female or anime")

        return argument.lower()

class PfpFormat(commands.Converter):
    async def convert(
        self,
        ctx,
        argument: str 
    ):
        formats = ['png', 'gif']   
        if not argument.lower() in formats: 
            raise commands.BadArgument("Formats can be: png or gif") 
        
        return argument.lower()