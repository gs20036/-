import discord
from discord.ext import commands, tasks
import random
import config
import pickle
from datetime import datetime
intents = discord.Intents.all()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents = intents)
bot.remove_command('help')
client = discord.Client(intents = intents)

def is_integer(a: str):
  try:
    value = int(a)
  except ValueError:
    return False
  return True

def dump_pickle(filename: str, data):
  try:
    with open(filename, 'wb') as f:
      pickle.dump(data, f)
  except:
    return

def open_pickle(filename: str, default = {}):
  ret = default
  try:
    with open(filename, 'rb') as f:
      ret = pickle.load(f)
  except:
    with open(filename, 'wb') as f:
      pickle.dump(ret, f)
  return ret

### 숫자야구 변수
number_baseball_on = False
number_baseball_answer = ""
number_baseball_tries = 0

def number_baseball_legit(content):
  if not is_integer(content):
    return False
  if len(content) != 4:
    return False
  for i in range(4):
    for j in range(i+1, 4):
      if content[i] == content[j]:
        return False
  return True
@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))
  check_new_day.start()

async def on_new_day(year, month, day):
  ctx = bot.get_channel(1071000052715225091)
  await ctx.send('>>> 라멘')
  await ctx.send('>>> 오늘은 ' + str(year) + '년 ' + str(month) + '월 ' + str(day) + '일입니다.')
  attend = open_pickle('attend.p', {})
  for id in attend:
    if id['today'] == 0:
      id['streak'] = 0
    id['today'] = 0
  dump_pickle('attend.p', attend)
  

@tasks.loop(seconds=1)
async def check_new_day():
  now = datetime.now()
  dat = open_pickle('days.p', set())
  if (now.year, now.month, now.day) not in dat:
    dat.add((now.year, now.month, now.day))
    await on_new_day(now.year, now.month, now.day)
    dump_pickle('days.p', dat)

@bot.command()
async def 명령어(ctx):
  if not ctx.channel.id == 1076344394388615168 and not ctx.channel.id == 1071000052715225091:
    return
  await ctx.send('>>> == 일반 명령어 ==\n!명령어, !출첵\n\n== 숫자야구 명령어 ==\n !숫자야구시작, !숫자야구포기')

@bot.command()
async def 숫자야구시작(ctx):
  if not ctx.channel.id == 1076344394388615168:
    return
  global number_baseball_on, number_baseball_answer, number_baseball_tries
  if ctx.author.bot:
    return
  if number_baseball_on:
    await ctx.send('>>> 이미 게임이 진행 중입니다.')
    return
  number_baseball_on = True
  answer_pool = [str(i) for i in range(10)]
  number_baseball_tries = 0
  for i in range(4):
    idx = random.randrange(0, 10 - i)
    number_baseball_answer = number_baseball_answer + str(answer_pool[idx])
    answer_pool.pop(idx)
  await ctx.send('>>> 숫자야구게임을 시작합니다.')

@bot.command()
async def 숫자야구포기(ctx):
  if not ctx.channel.id == 1076344394388615168:
    return
  global number_baseball_on, number_baseball_answer, number_baseball_tries
  if not number_baseball_on:
    return
  await ctx.send('>>> 정답: '+ number_baseball_answer)
  number_baseball_on = False
  number_baseball_answer = ""
  number_baseball_tries = 0

@bot.event
async def on_message(msg):
  global number_baseball_on, number_baseball_answer, number_baseball_tries
  content = msg.content
  print(content, number_baseball_legit(content))
  if number_baseball_legit(content) and number_baseball_on and msg.channel.id == 1076344394388615168:
    print('legit')
    number_baseball_tries += 1
    strikes = 0
    balls = 0
    answer_content = [0 for i in range(10)]
    guess_content = [0 for i in range(10)]

    for i in range(4):
      answer_content[int(number_baseball_answer[i])] += 1
      guess_content[int(content[i])] += 1
      if number_baseball_answer[i] == content[i]:
        strikes += 1

    for i in range(10):
      balls += min(answer_content[i], guess_content[i])
    balls -= strikes

    if strikes == 0 and balls == 0:
      await msg.channel.send('>>> 아웃!!\n\n남은기회 ' + str(10 - number_baseball_tries) + '번')
      if number_baseball_tries == 10:
        await msg.channel.send('>>> 실패!\n정답: ' + number_baseball_answer)
        number_baseball_on = False
        number_baseball_answer = ""
        number_baseball_tries = 0
    elif strikes == 4:
      await msg.channel.send('>>> 정답입니다!\n게임을 종료합니다.')
      number_baseball_on = False
      number_baseball_answer = ""
      number_baseball_tries = 0
    else:
      await msg.channel.send('>>> ' + str(strikes) + ' 스트라이크\n' + str(balls) + ' 볼\n\n남은기회 ' + str(10 - number_baseball_tries) + '번')
      if number_baseball_tries == 10:
        await msg.channel.send('>>> 실패!\n정답: ' + number_baseball_answer)
        number_baseball_on = False
        number_baseball_answer = ""
        number_baseball_tries = 0
  await bot.process_commands(msg)


@bot.command(aliases = ['ㅊㅊ'])
async def 출첵(ctx):
  if ctx.author.bot:
    return
  if not ctx.channel.id == 1071000052715225091:
    return
  attend = open_pickle('attend.p', {})
  id = ctx.author.id
  if id not in attend:
    attend[id] = {'total': 0, 'streak': 0, 'today': 0}
  if attend[id]['today'] != 0:
    now = datetime.now()
    seconds = now.hour() * 3600 + now.minute() * 60 + now.second()
    seconds = 86400 - seconds
    await ctx.replay('>>> 이미 출첵을 하셨습니다.\n' + str(seconds/3600) + '시간 ' + str((seconds/60)%60) + '분 ' + str(seconds%60) + '초 뒤에 출첵할 수 있습니다.')
    return
  attend[id]['today'] = 1
  attend[id]['total'] += 1
  attend[id]['streak'] += 1
  await ctx.reply('>>> 라멘')
  await ctx.reply('>>> 출첵되었습니다.\n\n총 출첵 횟수: ' + str(attend[id]['total']) + '회\n연속 출첵 횟수: ' +str(attend[id]['streak']) + '회')
  dump_pickle('attend.p', attend)

if __name__ == "__main__":
  bot.run(config.token_games)