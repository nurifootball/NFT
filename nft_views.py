from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from core import models as core_models
from django.utils import translation
from nft import models as nft_models
from django.http import JsonResponse
from users import transaction_view
from NuriAdmin import models as Admin_models
import random
import json
from django.views.generic import ListView

from utils import care_set
from utils.abi import ERC721


def main(request):
    lots_obj = nft_models.NFTLotsInformation.objects.first()
    owner_ERC20 = Admin_models.NuriAdminAddress.objects.get(
        token_kind="ERC20"
    )
    is_main = Admin_models.ServerInspection.objects.first().is_main
    return render(request, "PC_220112ST/nft/nft_draw.html",{
        "lots_obj":lots_obj,
        "owner_ERC20":owner_ERC20,
        "is_main":is_main
    })


def save(request):
    token_abi = json.dumps(ERC721.NuriAbi['ABI'])
    token = Admin_models.NuriAdminAddress.objects.get(
        token_kind="ERC721",
    )
    token.abi = token_abi
    token.save()
    return JsonResponse({"result":True})


@login_required(login_url="users:login")
def request_lots_basic_card(request):
    """
    NFT 뽑기 시 유저 request를 기록.
    저장 내용
    from_address : 요청 유저
    to_address : owner_wallet
    tx_hash : Deposit Transaction의 hash 값
    amount : 뽑기하기 위해 송금한 NRFB 수량
    lots_count : 뽑기을 수량
    lots_id : 뽑기 신청한 해당 뽑기
    """
    if request.user.is_authenticated:
        if request.method == "POST":
            if int(request.user.basic_lots_count) > 0:
                lots_id = request.POST.get("lots_id")
                lots_type = request.POST.get("type")
                if not lots_type == "Basic":
                    return JsonResponse({"result":False})
                user = request.user
                lots_count = request.POST.get("lots_count")
                if int(lots_count) > int(request.user.basic_lots_count):
                    return JsonResponse({"reslut": False, "msg": "over count"})
                request.user.basic_lots_count -= int(lots_count)
                request.user.save()
                lots_history = nft_models.NFTLotsHistory.objects.create(
                    lots_user = user,
                    lots_count=lots_count,
                    lots_type = "Basic",
                )
                try:
                    lots_obj = nft_models.NFTLotsInformation.objects.get(
                        id = lots_id
                    )

                except Exception as e:
                    lots_history.is_result = False
                    lots_history.save()
                    """
                        에러 발생 넣기
                    """
                    return JsonResponse({"result":False})
                lots_history.lots_obj = lots_obj
                lots_history.save()
                lots_card_list = list()

                for i in range(int(lots_count)):
                    new_card = care_set.make_card("Basic")
                    lots_card_list.append(new_card)

                    nft_models.LotsCardList.objects.create(
                        lots_history=lots_history,
                        lots_card=new_card,
                        is_pending = False
                    )

                    nft_models.NFTCard.objects.create(
                        nft_owner=request.user,
                        nft_info=new_card,

                        token_id=None,
                        is_nft=False,

                        is_mint = False,
                        change_owner_history = "",

                    )

                return JsonResponse({
                        "result":True,
                        "lots_id":lots_history.id
                     })
            else:
                return JsonResponse({"reslut":False,"msg":"over count"})
        else:
            return JsonResponse({"result":False})
    else:
        return JsonResponse({"result":False})


@login_required(login_url="users:login")
def request_lots_NRFB_point(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        if int(request.user.NRFB) >= int(amount):
            lots_count = request.POST.get("lots_count")
            lots_id = request.POST.get("lots_obj_id")
            lots_history = nft_models.NFTLotsHistory.objects.create(
                amount=int(amount),
                lots_count=lots_count,
                lots_type="NFT",
                lots_user=request.user,
                is_point_pay = True
            )

            try:
                lots_obj = nft_models.NFTLotsInformation.objects.get(
                    id=lots_id
                )
            except Exception as e:
                raise Exception
            lots_history.lots_obj = lots_obj
            lots_history.save()
            lots_card_list = list()
            for i in range(int(lots_count)):
                new_card = care_set.make_card("NFT")
                lots_card_list.append(new_card)

                new_nft_card = nft_models.NFTCard.objects.create(
                    nft_owner=request.user,
                    nft_info=new_card,
                    token_id=None,
                    is_burn=False,
                    is_nft=True
                )

                nft_models.LotsCardList.objects.create(
                    lots_history=lots_history,
                    lots_card=new_card,
                    is_nft=True
                )
            request.user.NRFB -= int(amount)
            request.user.save()


            return JsonResponse({
                "result": True,
                "lots_id": lots_history.id
            })
        else:
            return JsonResponse({
                "result": False
            })
    else:
        return JsonResponse({
                "result": False
            })


@login_required(login_url="users:login")
def request_lots_NRFB_card(request):
    """
    NFT 뽑기 시 유저 request를 기록.
    저장 내용
    from_address : 요청 유저
    to_address : owner_wallet
    tx_hash : Deposit Transaction의 hash 값
    amount : 뽑기하기 위해 송금한 NRFB 수량
    lots_count : 뽑기을 수량
    lots_id : 뽑기 신청한 해당 뽑기
    """
    if request.method == "POST":
        from_address = request.POST.get("from_address")
        to_address = request.POST.get("to_address")
        tx_hash = request.POST.get("tx_hash")
        amount = request.POST.get("amount")
        lots_count = request.POST.get("lots_count")
        lots_id = request.POST.get("lots_obj_id")

        lots_history = nft_models.NFTLotsHistory.objects.create(
            from_address=from_address,
            to_address=to_address,
            tx_hash=tx_hash,
            amount=int(amount),
            lots_count=lots_count,
            lots_type = "NFT",
            lots_user = request.user
        )

        try:
            lots_obj = nft_models.NFTLotsInformation.objects.get(
                id = lots_id
            )
        except Exception as e:
            raise Exception
        lots_history.lots_obj = lots_obj
        lots_history.save()
        lots_card_list = list()
        for i in range(int(lots_count)):
            new_card = care_set.make_card("NFT")
            lots_card_list.append(new_card)

            new_nft_card = nft_models.NFTCard.objects.create(
                nft_owner=request.user,
                nft_info=new_card,
                token_id=None,
                is_burn=False,
                is_nft = True
            )

            nft_models.LotsCardList.objects.create(
                lots_history = lots_history,
                lots_card = new_card,
                is_nft = True
            )
        return JsonResponse({
            "result":True,
            "lots_id":lots_history.id
        })
    else:
        return JsonResponse({
            "result":False
        })


@login_required(login_url="users:login")
def nft_draw_result(request,pk):
    if request.method == "GET":
        try:
            lots_history = nft_models.NFTLotsHistory.objects.get(
                id = pk,
                lots_user = request.user,
            )
            NFT_list =  nft_models.LotsCardList.objects.filter(
                lots_history = lots_history
            )
            rate_counts = list()

            for NFT_obj in NFT_list:
                rate_break = True

                r_count = nft_models.LotsCardList.objects.filter(
                    lots_history=lots_history,
                    lots_card__rate__rate = NFT_obj.lots_card.rate.rate
                ).count()
                if rate_counts:
                    for rate_count in rate_counts:
                        if rate_count['rate'] == NFT_obj.lots_card.rate.rate:
                            rate_break = False
                            break
                if rate_break:
                    rate_counts.append({
                        "rate":NFT_obj.lots_card.rate.rate,
                        "count":r_count
                    })
            return render(request,"PC_220112ST/nft/nft_draw_result.html",{
                "NFT_list":NFT_list,
                "rate_count":rate_counts,
            })
        except Exception as e:
            Admin_models.AdminDoError.objects.create(
                error_str = f"nft_draw_result : {str(e)}"
            )
            return redirect("core:main")
    else:
        Admin_models.AdminDoError.objects.create(
            error_str=f"nft_draw_result : 비정상적 접근 {request.user}"
        )
        return redirect("core:main")


def save_lots_history(request):

    if request.user.is_anonymous:
        return

    if request.method == "POST":
        request_amount = request.POST.get("request_amount")
        lots_obj = nft_models.NFTLotsInformation.objects.first()
        request_amount = int(request_amount)
        lots_rate_obj = nft_models.NFTRate.objects.filter(
            is_lots = True
        )
        lots_team = nft_models.NFTTeam.objects.filter(
            is_can_lots = True
        )
        if (request_amount * int(lots_obj.price)) > request.user.NRFB:
            return JsonResponse({"result": "보유 NRFB가 모자랍니다"})

        for i in range(request_amount):
            weights = []
            for lots_rate in lots_rate_obj:
                weight = int(lots_rate.lots_rate * 100000)
                weights.append(weight)
            cho = random.choices(lots_rate_obj, weights, k=1)
            team = random.choice(lots_team)
            position = random.choice(nft_models.NFTCardSetInfo.position)
            pass


    return JsonResponse({"result" :True})


def nft_detail(request, pk):

    NFT_obj = nft_models.NFTCard.objects.get(
        id = pk
    )

    return render(request,"PC_220112ST/nft/nft_detail.html",{
        "NFT_obj":NFT_obj
    })


@login_required(login_url="users:login")
def nft_purchase(request,pk):
    NFT_obj = nft_models.NFTCard.objects.get(
        id = pk
    )

    context={
        "NFT_obj":NFT_obj
    }

    return render(request,"PC_220112ST/nft/nft_purchase.html",context)


@login_required(login_url="users:login")
def open_random_box(request,pk):
    try:
        no_open_card = nft_models.NFTCard.objects.get(
            nft_owner = request.user,
            id = pk,
            is_open = False,
        )

        lots_history = nft_models.NFTLotsHistory.objects.create(
            amount= 0,
            lots_count= 1,
            lots_type="Distribute",
            lots_user=request.user,
            is_point_pay=True
        )

        new_card = care_set.make_card("NFT")

        no_open_card.nft_info = new_card
        no_open_card.is_open = True
        no_open_card.save()


        NFT_obj = nft_models.LotsCardList.objects.create(
            lots_history=lots_history,
            lots_card=new_card,
            is_nft=True
        )
        NFT_list = list()
        NFT_list.append(NFT_obj)
        rate_counts = list()

        for NFT_obj in NFT_list:
            rate_break = True

            r_count = nft_models.LotsCardList.objects.filter(
                lots_history=lots_history,
                lots_card__rate__rate=NFT_obj.lots_card.rate.rate
            ).count()

            if rate_counts:
                for rate_count in rate_counts:
                    if rate_count['rate'] == NFT_obj.lots_card.rate.rate:
                        rate_break = False
                        break
            if rate_break:
                rate_counts.append({
                    "rate": NFT_obj.lots_card.rate.rate,
                    "count": r_count
                })

        return render(request, "PC_220112ST/nft/nft_draw_result.html", {
            "NFT_list": NFT_list,
            "rate_count": rate_counts,
        })
    except Exception as e:
        Admin_models.AdminDoError.objects.create(
            error_str=f"open_random_box : {str(e)}"
        )
        return redirect("core:main")
