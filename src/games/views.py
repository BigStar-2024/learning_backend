import json

from django.http import HttpResponse
from django.core.files import File
from django.conf import settings
import lxml.html as LH
from graphql_jwt.utils import (jwt_decode, refresh_has_expired)
from django.contrib.auth import get_user_model
from games.models import Game
from wallets.models import CoinWallet
from .models import PlayGameTransaction
from django.contrib.auth.models import User

import os
import lxml.html as LH

User = get_user_model()

def game_loader(request, folder_name):
    print("game loader")
    token = request.GET['token'];
    id = ""
    contents = "Game Not Found!"
    game = ""
    path = ""
    user = None
    student = None
    account = None
    # --------------------- Get user and game from DB -S--------------------------#
    try:
        payload = jwt_decode(token)
        if (refresh_has_expired(payload['exp'])) :
            raise Exception("Token has expired")
        id = payload['sub']
        # Get User By Id
        user = User.objects.get(pk=int(id))
        # Get Student From User
        student = user.student
        # Get Wallet of Student
        account, new = CoinWallet.objects.get_or_create(student=student)
        # Get Game by Folder Name
        game = Game.objects.get(path = folder_name)
        path = settings.MEDIA_ROOT + "games/" + game.path + "/" + game.random_slug+"_index.html"

        # if the kid has classroom, then set the game price acording to the classroom settings
        game_price_percentage = student.classroom.game_cost_percentage if hasattr(student, 'classroom') else 100
        game_price = game_price_percentage*game.cost/100

        game_allowed = student.classroom.enable_games if hasattr(student, 'classroom') else True
    
    except Exception as e:
        print(e)
        return HttpResponse(contents)

    if game_allowed is not True:
        contents = "Your class is not allowed to play games!"
        return HttpResponse(contents)

    if account.balance < game_price:
        contents = "You don't have enough coins"
        return HttpResponse(contents)
    # --------------------- Get user and game from DB -E--------------------------#
    
    # --------------- Change the index.html file name to randomg slug name -S----------------#    
    if not os.path.exists(path) :
        initial_path = settings.MEDIA_ROOT + "games/" + game.path + "/"
        if os.path.exists(initial_path + "index.html") :
            initial_path = initial_path + "index.html"
        elif os.path.exists(initial_path + "index.htm") :
            initial_path = initial_path + "index.html"
        else : 
            return HttpResponse(contents)
        # Add permission to rename file
        # os.chmod(initial_path, 0o0777)
        # Rename index.html to random name
        os.rename(initial_path, path)
    # --------------- Change the file name  (index.html) to randomg slug name -E----------------#  

    # if account.balance > game_price:
        # ----------- Deduct Coin from Wallet -S------------------------ #
    play_game_transaction = PlayGameTransaction(
        game=game,
        account=account,
    )
    play_game_transaction.save(price=game_price_percentage)
    game.play_stats += 1
    game.save()
    # ----------- Deduct Coin from Wallet -E------------------------ #

    # --------------- Read Content of index.html file -S---------------------#
    file = open(path, 'r')
    contents =file.read()
    file.close()
    # --------------- Read Content of index.html file -E---------------------#   
    # else:
        # contents = "You don't have enough coins"
    return HttpResponse(contents)