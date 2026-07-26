from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages

# Create your views here.
def home(request):
    '''simple homepage + contact enquiry page form'''
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        message = request.POST.get('message')
        if name and email and mobile and message:
            Enquiry.objects.create(name=name,email=email,mobile=mobile,message=message)
            messages.success(request,'Your enquiry has been submitted successfully!')
            return redirect('home')  #Redirect to homepage after submission
        else:
            messages.error(request,'Please fill in all fields.')
    return render(request,'home.html')

def about(request):
    return render(request,'about.html')

from django.contrib.auth import authenticate, login, logout

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and getattr(user,'role',None) == 'ADMIN':
            login(request,user)
            messages.success(request,'Logged in successfully')
            return redirect('admin_dashboard')
        else:
            messages.error(request,'Invalid credential and not a Admin!')
    return render(request,'admin_login.html')

def admin_required(view_func):
    '''Decorator to restrict access to admin user only'''
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user,'role',None)!='ADMIN':
            messages.error(request,'You must be an admin to access this page')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def member_required(view_func):
    '''Decorator to restrict access to member user only'''
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user,'role',None)!='MEMBER':
            messages.error(request,'You must be an admin to access this page')
            return redirect('member_login')
        return view_func(request, *args, **kwargs)
    return wrapper

@admin_required
def admin_dashboard_view(request):
    total_members = MemberProfile.objects.count()
    active_memberships = MemberProfile.objects.filter(membership_end__gte=timezone.now().date()).count()
    today_registrations = MemberProfile.objects.filter(join_date=timezone.now().date()).count()
    pending_payments = Payment.objects.filter(status='PENDING').count()
    return render(request,'admin_dashboard.html',{
        'total_members':total_members,
        'active_memberships':active_memberships,
        'today_registrations':today_registrations,
        'pending_payments':pending_payments,
    })

def logout_view(request):
    logout(request)
    messages.info(request,'Logged out successfully.')
    return redirect('home')

# admin planning detail here
@admin_required
def admin_plans_list(request):
    plans = MembershipPlan.objects.all().order_by('duration_months')
    return render(request, 'admin_plans_list.html',{'plans':plans})

@admin_required
def admin_plan_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        duration_months = request.POST.get('duration_months')
        fee = request.POST.get('fee')
        description = request.POST.get('description')

        if name and duration_months and fee:
            MembershipPlan.objects.create(
                name = name,
                duration_months = duration_months,
                fee = fee,
                description = description
            )
            messages.success(request,'Membership plan added successfully')
            return redirect('admin_plans_list')
        else:
            messages.error(request,'Please fill in all required field')
    return render(request,'admin_plan_form.html',{'mode':'add'})

@admin_required
def admin_plan_edit(request,plan_id):
    plan = MembershipPlan.objects.get(id=plan_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        duration_months = request.POST.get('duration_months')
        fee = request.POST.get('fee')
        description = request.POST.get('description')

        if name and duration_months and fee:
            plan.name = name
            plan.duration_months = duration_months
            plan.fee = fee
            plan.description = description
            plan.save()
            messages.success(request,'Membership plan updated successfully!')
            return redirect('admin_plans_list')
        else:
            messages.error(request,'Please fill in all required fields.')
    return render(request,'admin_plan_form.html',{'plan':plan, 'mode':'edit'})

@admin_required
def admin_plan_delete(request,plan_id):
    plan = MembershipPlan.objects.get(id=plan_id)
    if request.method == 'POST':
        plan.delete()
        messages.success(request,'Membership plan deleted successfully!')
        return redirect('admin_plans_list')
    return redirect('admin_plans_list')

#Trainer detail here
@admin_required
def admin_trainer_list(request):
    trainer = Trainer.objects.all().order_by('name')
    return render(request, 'admin_trainers_list.html', {'trainers': trainer})

@admin_required
def admin_trainer_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        specialization = request.POST.get('specialization')
        shift_timing = request.POST.get('shift_timing')

        if name and mobile and specialization and shift_timing:
            Trainer.objects.create(
                name = name,
                mobile = mobile,
                specialization = specialization,
                shift_timing = shift_timing
            )
            messages.success(request, 'Trainer added successfully')
            return redirect('admin_trainer_list')
        else:
            messages.error(request,'Please fill in all required fields.')
    return render(request,'admin_trainer_form.html',{'mode':'add'})

@admin_required
def admin_trainer_edit(request,trainer_id):
    trainer = Trainer.objects.get(id=trainer_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        specialization = request.POST.get('specialization')
        shift_timing = request.POST.get('shift_timing')

        if name and mobile and specialization and shift_timing:
            trainer.name = name
            trainer.mobile = mobile
            trainer.specialization = specialization
            trainer.shift_timing = shift_timing
            trainer.save()
            messages.success(request, 'Trainer Updated successfully')
            return redirect('admin_trainer_list')
        else:
            messages.error(request, 'Please fill in all required fields')
    return render(request, 'admin_trainer_form.html',{'trainer': trainer, 'mode':'edit'})

@admin_required
def admin_trainer_delete(request,trainer_id):
    trainer = Trainer.objects.get(id=trainer_id)
    if request.method == 'POST':
        trainer.delete()
        messages.success(request, 'Trainer deleted successfully!')
        return redirect('admin_trainer_list')
    return redirect('admin_trainer_list')

#Member detail here
@admin_required
def admin_member_list(request):
    search = request.GET.get('search','')
    members = MemberProfile.objects.all().select_related('user','plan')
    if search:
        members = members.filter(full_name__icontains=search)
    return render(request,'admin_member_list.html',{'members':members,'search':search})

@admin_required
def admin_member_add(request):
    plans = MembershipPlan.objects.all().order_by('duration_months')
    trainer = Trainer.objects.all().order_by('name')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        join_date = request.POST.get('join_date') or timezone.now().date()

        plan_id = request.POST.get('plan_id')
        trainer_id = request.POST.get('trainer_id')

        if User.objects.filter(username=username).exists():
            messages.error(request,'Username already exists. Please choose different Username')
            return redirect('admin_member_add')
        
        user = User.objects.create_user(username=username, password=password,role='MEMBER')
        
        plan = MembershipPlan.objects.get(id=plan_id) if plan_id else None

        trainer = Trainer.objects.get(id=trainer_id) if trainer_id else None

        MemberProfile.objects.create(
            user = user,
            full_name = full_name,
            mobile = mobile,
            age = age,
            gender = gender,
            address = address,
            join_date = join_date,
            plan = plan,
            trainer = trainer
        )
        messages.success(request, 'Member added successfully!')
        return redirect('admin_member_list')
    return render(request,'admin_member_form.html', {'plans': plans, 'trainers': trainer, 'mode':'add'})

@admin_required
def admin_member_edit(request,member_id):
    member = MemberProfile.objects.get(id=member_id)
    plans = MembershipPlan.objects.all().order_by('duration_months')
    trainers = Trainer.objects.all().order_by('name')
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        join_date = request.POST.get('join_date') or member.join_date
        plan_id = request.POST.get('plan_id')
        trainer_id = request.POST.get('trainer_id')

        plan = MembershipPlan.objects.get(id=plan_id) if plan_id else None
        trainer = Trainer.objects.get(id=trainer_id) if trainer_id else None

        member.full_name = full_name
        member.mobile = mobile
        member.age = age
        member.gender = gender
        member.address = address
        member.join_date = join_date
        member.plan = plan
        member.trainer = trainer
        member.save()
        messages.success(request, 'Member updated successfully!')
        return redirect('admin_member_list')
    return render(request,'admin_member_form.html',{ 'member':member, 'plans': plans, 'trainers': trainers, 'mode': 'edit'})

@admin_required
def admin_member_delete(request,member_id):
    member = MemberProfile.objects.get(id=member_id)
    if request.method == 'POST':
        user = member.user
        member.delete()
        user.delete()
        messages.success(request, 'Member deleted successfully!')
        return redirect('admin_member_list')
    return redirect('admin_members_list')

#Attendance detail here
@admin_required
def admin_attendance_list(request):
    today = timezone.now().date()
    date = request.GET.get('date') or today
    attendances = Attendance.objects.all().select_related('member').filter(date=date)
    members = MemberProfile.objects.all().order_by('full_name')
    member_id = request.GET.get('member_id')
    if member_id:
        attendances = attendances.filter(member_id=member_id)
    return render(request,'admin_attendance_list.html',{'attendances':attendances,'members':members,'today':today,'selected_member_id':member_id,'selected_date':date})

@admin_required
def admin_attendance_add(request):
    members = MemberProfile.objects.all().order_by('full_name')

    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        date = request.POST.get('date')
        time_in = request.POST.get('time_in')

        if not member_id:
            messages.error(request,"Please select a member.")
            return redirect('admin_attendance_add')
        member = MemberProfile.objects.get(id=member_id)
        attendance, created = Attendance.objects.get_or_create(
            member=member, date=date, time_in=time_in
        )

        if not created:
            attendance.time_in = time_in
            attendance.save()
            messages.info(request,'Attendance updated successfully!')
        messages.success(request,'Attendance record successfully!')
    return render(request,'admin_attendance_form.html',{'members': members})

#Equipment
@admin_required
def admin_equipment_list(request):
    equipments = Equipment.objects.all().order_by('name')
    return render(request,'admin_equipment_list.html',{'equipments':equipments})

@admin_required
def admin_equipment_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        units = request.POST.get('units')
        price = request.POST.get('price')
        purchase_date = request.POST.get('purchase_date') or timezone.now().date()

        if name and units and price:
            Equipment.objects.create(
                name = name,
                units = units,
                price = price,
                purchase_date = purchase_date
            )
            messages.success(request, 'Equipment added successfully!')
            return redirect('admin_equipment_list')
        else:
            messages.error(request,'Please fill in all required fields')
    return render(request,'admin_equipment_form.html',{'mode':'add'})

@admin_required
def admin_equipment_edit(request,equipment_id):
    equipment = Equipment.objects.get(id=equipment_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        units = request.POST.get('units')
        price = request.POST.get('price')
        purchase_date = request.POST.get('purchase_date') or equipment.purchase_date

        if name and units and price:
            equipment.name = name
            equipment.units = units
            equipment.price = price
            equipment.purchase_date = purchase_date
            equipment.save()
            messages.success(request,'Equipmnet updated successfully!')
            return redirect('admin_equipment_list')
        else:
            messages.error(request,'Please fill in all required fields')
    return render(request, 'admin_equipment_form.html',{'equipment':equipment,'mode':'edit'})

@admin_required
def admin_equipment_delete(request,equipment_id):
    equpment = Equipment.objects.get(id=equipment_id)

    if request.method == 'POST':
        equpment.delete()
        messages.success(request, 'Equipment deleted successfully!')
        return redirect('admin_equipment_list')
    return redirect('admin_equipment_list')

#Enquiry
@admin_required
def admin_enquiries_list(request):
    enquiries = Enquiry.objects.all().order_by('-created_at')
    return render(request,'admin_enquiry_list.html',{'enquiries':enquiries})

@admin_required
def admin_enquiry_update_status(request,enquiry_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        enquiry = Enquiry.objects.get(id=enquiry_id)
        if status in ['NEW','SEEN','RESOLVED']:
            enquiry.status = status
            enquiry.save()
            messages.success(request,'Enquiry status updated')
    return redirect('admin_enquiries_list')

#Workout Plans
@admin_required
def admin_workout_plans_list(request):
    member_id = request.GET.get('member_id')
    workout_plans = WorkoutPlan.objects.select_related('member').all().order_by('-created_at')
    if member_id:
        workout_plans = workout_plans.filter(member_id=member_id)
    members = MemberProfile.objects.all().order_by('full_name')
    return render(request,'admin_workout_plans_list.html',{'workout_plans':workout_plans,'members':members,'selected_member_id':member_id})

@admin_required
def admin_workout_plan_add(request):
    members = MemberProfile.objects.all().order_by('full_name')
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        title = request.POST.get('title')
        description = request.POST.get('description')

        if not member_id or not title or not description:
            messages.error(request,'Please select a member and enter plan details.')
            return redirect('admin_workout_plan_add')
        member = MemberProfile.objects.get(id=member_id)

        WorkoutPlan.objects.create(
            member = member,
            title = title,
            description = description
        )
        messages.success(request,'Workout plan added successfully')
        return redirect('admin_workout_plans_list')
    return render(request,'admin_workout_plan_form.html',{'members':members})

@admin_required
def admin_workout_plan_delete(request,plan_id):
    plan = WorkoutPlan.objects.get(id=plan_id)
    if request.method == 'POST':
        plan.delete()
        messages.success(request,'Workout plan deleted successfully!')
        return redirect('admin_workout_plans_list')
    return redirect('admin_workout_plan_list')

@admin_required
def admin_payments_list(request):
    member_id = request.GET.get('member_id')
    status = request.GET.get('status')
    payments = Payment.objects.select_related('member','plan').all().order_by('payment_date')

    if member_id:
        payments = payments.filter(member__id = member_id)
    if status in ['PENDING','PAID']:
        payments = payments.filter(status = status)

    members = MemberProfile.objects.all().order_by('full_name')

    return render(request,'admin_payments_list.html',{'payments':payments, 'members':members, 'selected_member_id':member_id, 'selected_status':status})

from datetime import timedelta
@admin_required
def admin_payment_add(request):
    members = MemberProfile.objects.all().order_by('full_name')
    plans = MembershipPlan.objects.all().order_by('duration_months')

    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        plan_id = request.POST.get('plan_id')
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date') or timezone.now().date()
        mode = request.POST.get('mode')
        status = request.POST.get('status')
        notes = request.POST.get('notes')

        set_membership = request.POST.get('set_membership')
        membership_start = request.POST.get('membership_start')

        if not member_id or not plan_id or not amount or not status:
            messages.error(request,'Please fill in all required fields.')
            return redirect('amdin_payment_add')
        
        member = MemberProfile.objects.get(id=member_id)
        plan = MembershipPlan.objects.get(id=plan_id)

        #overpayment check
        if plan and plan.fee:
            total_paid = Payment.objects.filter(
                member=member, plan=plan,status='PAID'
            ).aggregate(total=models.Sum('amount'))['total'] or 0
            
            if float(total_paid) + float(amount) > float(plan.fee):
                remaining_amount = float(plan.fee) - float(total_paid)
                messages.error(request, f'Total paid amount exceeds the plan fee of {plan.fee}. Remaining amount: {remaining_amount}. Please check the amount.')
                return redirect('admin_payment_add')

        Payment.objects.create(
            member = member,
            plan = plan,
            amount = amount,
            status = status,
            mode = mode,
            payment_date = payment_date,
            notes = notes
        )

        if set_membership == 'on' and plan and membership_start:
            try:
                membership_start = timezone.datetime.strptime(membership_start,'%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid membership start date format. Please use YYYY-MM-DD.')
                return redirect('admin_payment_add')
            member.plan=plan
            member.membership_start = membership_start
            member.membership_end = membership_start + timedelta(days=plan.duration_months*30)
            member.save()

        messages.success(request,'Payment recorded successfully!')
        return redirect('admin_payments_list')
    return render(request, 'admin_payment_form.html',{'members':members,'plans':plans})

@admin_required
def admin_feedbacks_list(request):
    member_id = request.GET.get('member_id')
    feedbacks = Feedback.objects.select_related('member').all().order_by('-created_at')
    members = MemberProfile.objects.all().order_by('full_name')

    if member_id:
        feedbacks = feedbacks.filter(member_id=member_id)

    context = {
        'feedbacks': feedbacks,
        'members' : members,
        'selected_members_id' : int(member_id) if member_id else None,
    }
    return render(request, 'admin_feedbacks_list.html',context)

# member section
def member_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None and getattr(user,'role',None) == 'MEMBER':
            login(request,user)
            messages.success(request,'Logged in successfully')
            return redirect('member_dashboard')
        else:
            messages.error(request,'Invalid credentials or not an member.')
    return render(request,'member_login.html')

@member_required
def member_dashboard_view(request):
    member = request.user.member_profile
    total_attendance = member.attendances.count()
    total_payments = member.payment.count()
    workout_count = member.workout_plans.count()
    return render(request,'member_dashboard.html',{
        'member': member,
        'total_attendance': total_attendance,
        'total_payments': total_payments,
        'workout_count': workout_count
    })

@member_required
def member_attendance(request):
    member_profile = MemberProfile.objects.get(user=request.user)
    attendances = Attendance.objects.filter(member=member_profile).order_by('-date')
    return render(request,'member_attendance.html',{'attendances': attendances})

from django.db.models import Sum
@member_required
def member_membership(request):
    member = request.user.member_profile

    days_remaining = None
    total_paid = 0
    remaining = None
    membership_status = "No Membership"

    if member.membership_end:
        days_remaining = (member.membership_end - timezone.now().date()).days

        if days_remaining <=0:
            days_remaining = 0
            membership_status = "Membership Ended"
        else:
            membership_status = "Active"

    if member.plan:
        agg = Payment.objects.filter(
            member = member,
            plan = member.plan,
            status = 'PAID'
        ).aggregate(total=Sum('amount'))

        total_paid = agg['total'] or 0

        if member.plan.fee:
            remaining = float(member.plan.fee) - float(total_paid)

    context = {
        'member' : member,
        'membership_status' : membership_status,
        'days_remaining' : days_remaining,
        'total_paid' : total_paid,
        'remaining' : remaining
    }
    return render(request, 'member_membership.html',context)

@member_required
def member_payments(request):
    member_profile = MemberProfile.objects.get(user=request.user)
    payments = Payment.objects.filter(member=member_profile).select_related('plan').order_by('-payment_date')
    return render(request,'member_payments.html',{'payments':payments})

@member_required
def member_workout_plans(request):
    member_profile = MemberProfile.objects.get(user=request.user)
    workout_plans = WorkoutPlan.objects.filter(member=member_profile).order_by('-created_at')
    return render(request,'member_workout_plans.html',{'workout_plans':workout_plans})

@member_required
def member_profile(request):
    member = request.user.member_profile
    return render(request,"member_profile.html",{'member': member})

@member_required
def member_profile_edit(request):
    member = request.user.member_profile
    if request.method == 'POST':
        member.full_name = request.POST.get('full_name')
        member.mobile = request.POST.get('mobile')
        member.age = request.POST.get('age')
        member.gender = request.POST.get('gender')
        member.address = request.POST.get('address')
        member.save()
        messages.success(request,'Profile updated successfully')
        return redirect('member_profile')
    return render(request, 'member_profile_edit.html', {'member': member})

@member_required
def member_change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request,'Current Password is incorrect')
            return redirect('member_change_password')

        if new_password != confirm_password:
            messages.error(request, 'Current Password is incorrect')
            return redirect('member_change_password')

        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, 'Password changed successfully! Please log in again')
        return redirect('member_login')
    return render(request, 'member_change_password.html')

@member_required
def member_feedback(request):
    member = request.user.member_profile
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            Feedback.objects.create(member=member, message=message)
            messages.success(request, 'Your feedback has been submitted successfully!')
            return redirect('member_feedback') #redirect to feedback page after submitted
        else:
            messages.error(request, 'Please enter your feedback before submitting.')
    feedbacks = member.feedback.all().order_by('-created_at')
    return render(request, 'member_feedback.html',{'feedbacks': feedbacks})

