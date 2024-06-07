import asyncio
import json
import logging
import random
import sys

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command

logging.basicConfig(level=logging.INFO)
bot = Bot(token=sys.argv[1])
dp = Dispatcher()

with open("questions.json", "r", encoding="utf-8") as file:
	data = json.load(file)
	questions = data["questions"]

user_states = {}

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.reply("Привет! Добро пожаловать в викторину. Я буду задавать тебе вопросы, а ты должен будешь дать правильный ответ. Для запуска напиши слово Викторина")

@dp.message(F.text)
async def handle_text(message: types.Message):
	user_id = message.from_user.id

	if message.text.lower() == "викторина":
		if user_id not in user_states:
			user_states[user_id] = {
				"questions": list(questions.keys()),
				"asked_questions": [],
				"current_question": None,
				"score": 0
			}
		question = get_new_question(user_id)
		if question is None:
			await message.reply("Все вопросы заданы. Напиши 'Викторина', чтобы начать сначала.")
		else:
			answer = questions[question].lower()
			user_states[user_id]["current_question"] = {
				"question": question,
				"answer": answer
			}
			await message.reply("Вопрос: " + question)
		
	else:
		if user_id in user_states and "current_question" in user_states[user_id]:
			answer = user_states[user_id]["current_question"]["answer"]
			user_answer = message.text.lower()
			question = user_states[user_id]["current_question"]["question"]
      
			if user_answer == answer:
				user_states[user_id]["score"] += 1
				await message.reply("Правильно! Ответ: " + answer)
			else:
				await message.reply("Неправильно. Попробуй еще раз!")

			question = get_new_question(user_id)
			if question is None:
				await message.reply(f"Все вопросы заданы. Ваш результат {user_states[user_id]["score"]}. Напишите 'Викторина', чтобы начать сначала.")
			else:
				answer = questions[question].lower()
				user_states[user_id]["current_question"] = {
					"question": question,
					"answer": answer
				}
				await message.reply("Вот следующий вопрос: " + question)
		else:
			await message.reply("Напиши 'Викторина', чтобы начать викторину.")

def get_new_question(user_id):
    available_questions = user_states[user_id]["questions"]
    asked_questions = user_states[user_id]["asked_questions"]
    
    if len(available_questions) == len(asked_questions):
        return None

    question = random.choice([q for q in available_questions if q not in asked_questions])
    user_states[user_id]["asked_questions"].append(question)
    return question

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.info("Starting bot...")
    asyncio.run(main())
