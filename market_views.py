from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect
from . import models
from nft import models as nft_models
from NuriAdmin import models as Admin_modles
from django.http import JsonResponse
# Create your views here.


def main(request):
    context = dict()

    level = request.GET.get("level")
    po = request.GET.get('position')
    q = Q(is_selling = False)
    if level and not level == "All":
        q = q & Q(sell_card__nft_info__rate__rate=level)
    if po:
        q = q & Q(sell_card__nft_info__position__r_po=po)

    sell_list = models.SellList.objects.filter(q).order_by("-created")

    paginator = Paginator(sell_list, 9)
    page_num = request.GET.get('page')
    obj_count = sell_list.count()
    try:
        sell_list = paginator.page(page_num)
    except PageNotAnInteger:
        sell_list = paginator.page(1)
    except EmptyPage:
        sell_list = paginator.page(paginator.num_pages)

    if sell_list:
        index = sell_list.number - 1
        max_index = len(paginator.page_range)
        start_index = index - 4 if index >= 4 else 0
        if index < 4:
            end_index = 7 - start_index
        else:
            end_index = index + 5 if index <= max_index - 5 else max_index
        page_range = list(paginator.page_range[start_index:end_index])
        context["page_range"] = page_range

    rates = nft_models.NFTRate.objects.all()
    context["rates"] = rates
    context["obj_count"] = obj_count
    context["sell_list"] = sell_list

    return render(request,"PC_220112ST/nftmarket/nft_market.html",context)


@login_required(login_url="users:login")
def nft_sales(request,pk):
    context = dict()
    try:
        NFT_obj = nft_models.NFTCard.objects.get(
            id=pk,
            nft_owner = request.user,
            nft_owner__username = str(request.user),
            is_nft = True,
            is_mint = True,
            is_selling = False,
            is_out = False,
        )
        context["NFT_obj"] = NFT_obj
    except Exception as e:
        print(str(e))
        return redirect("core:main")
    if request.method == "POST":
        res_price = request.POST.get("NRFB_amount")
        seller = request.user
        is_selling = False
        NFT_obj.is_selling = None
        NFT_obj.save()

        new_sell_obj = models.SellList.objects.create(
            sell_card = NFT_obj,
            res_price = res_price,
            seller = seller,
            is_selling = is_selling
        )
        return redirect("nftmarket:nft_sell_detail",new_sell_obj.id)

    return render(request,"PC_220112ST/nftmarket/nft_sales.html",context)

#
#
def sell_detail(request,pk):
    try:
        sell_obj = models.SellList.objects.get(
            id = pk
        )
        context = {
            "sell_obj": sell_obj
        }

        return render(request, "PC_220112ST/nftmarket/nft_market_detail.html", context)

    except Exception as e:
        print(str(e))


@login_required(login_url="users:login")
def buy_nft(request,pk):
    context = dict()
    try:
        sell_obj = models.SellList.objects.get(id=pk)
        owner_ERC20 = Admin_modles.NuriAdminAddress.objects.get(
            token_kind = "ERC20"
        )
        context["owner_ERC20"] = owner_ERC20
        context["sell_obj"] = sell_obj
    except Exception as e:
        models.NFTTransactionError.objects.create(
            error_str=str(e),
            error_user=request.user
        )
        return
    if request.method == "POST":
        if request.POST.get("is_NRFB"):
            amount = request.POST.get('amount')
            from_address = request.POST.get('from_address')
            to_address = request.POST.get('to_address')
            tx_hash = request.POST.get('tx_hash')

            tr_history = models.NFTTransactionHistory.objects.create(
                buyer=request.user,
                transaction_info=sell_obj,
                is_NRFB = True,
                is_status= None,
                amount = int(amount),
                from_address = from_address,
                to_address = to_address,
                tx_hash = tx_hash
            )
            sell_obj.is_selling = None
            sell_obj.save()
            return JsonResponse({"result":True})
        else:
            if sell_obj.res_price <= request.user.NRFB:
                request.user.NRFB -= sell_obj.res_price
                request.user.save()

                sell_obj.sell_card.nft_owner = request.user
                sell_obj.sell_card.is_selling = False
                sell_obj.seller.NRFB += sell_obj.res_price
                sell_obj.is_selling = True
                sell_obj.sell_card.save()
                sell_obj.seller.save()
                sell_obj.save()

                tr_history = models.NFTTransactionHistory.objects.create(
                    buyer=request.user,
                    transaction_info=sell_obj,
                    is_status=True,
                    is_NRFB=False,
                )

                tr_history.is_status = True
                tr_history.save()

                return redirect('users:transaction_history','Buy',1)
            else:
                error = list()
                error.append({
                    "error": "error",
                    "message": "You don't own as much NRFB as you need for the price."
                })
                context["errors"] = error
                render(request,"PC_220112ST/nftmarket/nft_purchase.html",context)

    return render(request,"PC_220112ST/nftmarket/nft_purchase.html",context)
#
#
#
#
