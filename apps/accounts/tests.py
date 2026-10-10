from datetime import date
from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from apps.accounts.roles import (
    ROLE_ADMINISTRATOR,
    ROLE_FARM_MANAGER,
    ROLE_HARVEST_MANAGER,
    ROLE_SALES_MANAGER,
    ROLE_STAFF,
)
from apps.crops.models import Crop, Field, Planting
from apps.customers.models import Customer
from apps.harvests.models import Harvest
from apps.sales.models import Order, OrderItem, Payment

User = get_user_model()
TEST_PASSWORD = "Strong-Agriculture-52!"


class AccountFeatureTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", stdout=StringIO())

        cls.superuser = User.objects.create_superuser(
            username="trusted-root",
            email="root@example.test",
            password=TEST_PASSWORD,
        )
        cls.administrator = cls.create_role_user(
            "application-admin",
            ROLE_ADMINISTRATOR,
        )
        cls.farm_manager = cls.create_role_user(
            "farm-manager",
            ROLE_FARM_MANAGER,
        )
        cls.harvest_manager = cls.create_role_user(
            "harvest-manager",
            ROLE_HARVEST_MANAGER,
        )
        cls.sales_manager = cls.create_role_user(
            "sales-manager",
            ROLE_SALES_MANAGER,
        )
        cls.staff = cls.create_role_user("farm-staff", ROLE_STAFF)

        cls.crop = Crop.objects.create(
            crop_name="Tomatoes",
            maturity_days=60,
            unit="kg",
        )
        cls.field = Field.objects.create(
            field_name="North field",
            field_size=Decimal("1.00"),
        )
        cls.planting = Planting.objects.create(
            crop=cls.crop,
            field=cls.field,
            planting_qty_unit="seeds",
            quantity_planted=Decimal("20.00"),
            planting_date=date(2026, 1, 1),
        )
        cls.harvest = Harvest.objects.create(
            planting=cls.planting,
            harvesting_date=date(2026, 2, 1),
            quantity_harvested=Decimal("100.00"),
            unit="kg",
        )
        cls.customer = Customer.objects.create(
            customer_name="Mlimani Market",
            customer_phone="0712345678",
        )
        cls.order = Order.objects.create(
            customer=cls.customer,
            order_date=date(2026, 2, 2),
        )
        OrderItem.objects.create(
            order=cls.order,
            crop=cls.crop,
            harvest=cls.harvest,
            quantity=Decimal("10.00"),
            unit_price=Decimal("2000.00"),
            unit="kg",
        )
        Payment.objects.create(
            order=cls.order,
            amount_paid=Decimal("8000.00"),
            payment_date=date(2026, 2, 2),
        )

    @classmethod
    def create_role_user(cls, username, role, **kwargs):
        user = User.objects.create_user(
            username=username,
            password=TEST_PASSWORD,
            is_active=True,
            **kwargs,
        )
        user.groups.add(Group.objects.get(name=role))
        return user

    def login_as(self, user):
        self.client.force_login(user)

    def test_anonymous_user_is_redirected_from_protected_pages(self):
        protected_urls = (
            reverse("dashboard:dashboard"),
            reverse("crops:crop-list"),
            reverse("harvests:harvest-list"),
            reverse("customers:customer-list"),
            reverse("sales:order-list"),
            reverse("accounts:user-list"),
        )
        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith(reverse("accounts:login")))

    def test_authenticated_user_without_role_cannot_open_dashboard(self):
        unassigned = User.objects.create_user(
            username="unassigned-user",
            password=TEST_PASSWORD,
            is_active=True,
        )
        self.login_as(unassigned)
        self.assertEqual(
            self.client.get(reverse("dashboard:dashboard")).status_code,
            403,
        )
        self.assertEqual(self.client.get(reverse("accounts:profile")).status_code, 200)

    def test_login_honors_safe_next_and_rejects_external_redirects(self):
        login_url = reverse("accounts:login")
        intended_url = reverse("crops:crop-list")
        response = self.client.post(
            login_url,
            {
                "username": self.sales_manager.username,
                "password": TEST_PASSWORD,
                "next": intended_url,
            },
        )
        self.assertRedirects(
            response,
            intended_url,
            fetch_redirect_response=False,
        )

        self.client.logout()
        response = self.client.post(
            login_url,
            {
                "username": self.sales_manager.username,
                "password": TEST_PASSWORD,
                "next": "https://attacker.example/redirect",
            },
        )
        self.assertRedirects(
            response,
            reverse("dashboard:dashboard"),
            fetch_redirect_response=False,
        )

    def test_already_authenticated_user_is_redirected_from_login(self):
        self.login_as(self.staff)
        response = self.client.get(reverse("accounts:login"))
        self.assertRedirects(
            response,
            reverse("dashboard:dashboard"),
            fetch_redirect_response=False,
        )

    def test_invalid_login_uses_generic_credentials_error(self):
        response_existing = self.client.post(
            reverse("accounts:login"),
            {"username": self.staff.username, "password": "incorrect"},
        )
        response_unknown = self.client.post(
            reverse("accounts:login"),
            {"username": "not-a-real-account", "password": "incorrect"},
        )
        existing_errors = list(response_existing.context["form"].non_field_errors())
        unknown_errors = list(response_unknown.context["form"].non_field_errors())
        self.assertEqual(existing_errors, unknown_errors)
        self.assertTrue(existing_errors)

    def test_inactive_user_cannot_log_in_or_continue_a_session(self):
        inactive = User.objects.create_user(
            username="inactive-user",
            password=TEST_PASSWORD,
            is_active=False,
        )
        response = self.client.post(
            reverse("accounts:login"),
            {"username": inactive.username, "password": TEST_PASSWORD},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())

        self.client.force_login(self.staff)
        User.objects.filter(pk=self.staff.pk).update(is_active=False)
        response = self.client.get(reverse("dashboard:dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_logout_requires_post_and_ends_session(self):
        self.login_as(self.staff)
        logout_url = reverse("accounts:logout")
        self.assertEqual(self.client.get(logout_url).status_code, 405)

        response = self.client.post(logout_url, follow=True)
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertContains(response, "You have been signed out.")
        protected = self.client.get(reverse("dashboard:dashboard"))
        self.assertEqual(protected.status_code, 302)

    def test_logout_post_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.staff)
        profile_page = client.get(reverse("accounts:profile"))
        self.assertIn("csrftoken", profile_page.cookies)
        self.assertEqual(
            client.post(reverse("accounts:logout")).status_code,
            403,
        )

    def test_role_setup_is_idempotent_and_assigns_the_defined_matrix(self):
        call_command("setup_roles", stdout=StringIO())
        call_command("setup_roles", stdout=StringIO())

        roles = (
            (self.administrator, "crops.delete_crop", "auth.add_user"),
            (self.farm_manager, "sales.delete_order", "sales.add_payment"),
            (self.harvest_manager, "harvests.change_harvest", "crops.view_crop"),
            (self.sales_manager, "sales.add_payment", "customers.change_customer"),
            (self.staff, "sales.view_order", "customers.view_customer"),
        )
        for user, allowed_permission, expected_permission in roles:
            with self.subTest(user=user.username, permission=allowed_permission):
                self.assertTrue(user.has_perm(allowed_permission))
                self.assertTrue(user.has_perm(expected_permission))

        self.assertFalse(self.harvest_manager.has_perm("harvests.delete_harvest"))
        self.assertFalse(self.sales_manager.has_perm("sales.delete_order"))
        self.assertFalse(self.sales_manager.has_perm("crops.add_crop"))
        self.assertFalse(self.staff.has_perm("sales.view_payment"))
        self.assertFalse(self.farm_manager.has_perm("auth.view_user"))
        self.assertEqual(
            Group.objects.filter(name=ROLE_ADMINISTRATOR).count(),
            1,
        )

    def test_sales_manager_can_work_with_sales_but_cannot_mutate_production(self):
        self.login_as(self.sales_manager)
        self.assertEqual(
            self.client.get(reverse("customers:customer-list")).status_code,
            200,
        )
        self.assertEqual(self.client.get(reverse("sales:order-list")).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("sales:order-create")).status_code,
            200,
        )

        crop_create = self.client.post(
            reverse("crops:crop-create"),
            {
                "crop_name": "Unauthorized crop",
                "maturity_days": 30,
                "unit": "kg",
            },
        )
        harvest_update = self.client.post(
            reverse("harvests:harvest-update", args=(self.harvest.pk,)),
            {
                "harvesting_date": "2026-02-03",
                "quantity_harvested": "5",
                "notes": "",
            },
        )
        self.assertEqual(crop_create.status_code, 403)
        self.assertEqual(harvest_update.status_code, 403)
        self.assertFalse(Crop.objects.filter(crop_name="Unauthorized crop").exists())
        self.harvest.refresh_from_db()
        self.assertEqual(self.harvest.quantity_harvested, Decimal("100.00"))

    def test_harvest_manager_can_record_harvest_but_not_access_sales_or_accounts(self):
        self.login_as(self.harvest_manager)
        self.assertEqual(
            self.client.get(reverse("harvests:harvest-list")).status_code,
            200,
        )
        response = self.client.post(
            reverse("harvests:harvest-create", args=(self.planting.pk,)),
            {
                "harvesting_date": "2026-02-03",
                "quantity_harvested": "5.00",
                "notes": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Harvest.objects.filter(planting=self.planting).count(), 2)
        self.assertEqual(
            self.client.get(reverse("sales:order-list")).status_code,
            403,
        )
        self.assertEqual(
            self.client.get(reverse("accounts:user-list")).status_code,
            403,
        )

    def test_farm_manager_can_use_operations_but_not_user_management(self):
        self.login_as(self.farm_manager)
        self.assertEqual(self.client.get(reverse("crops:crop-list")).status_code, 200)
        response = self.client.post(
            reverse("customers:customer-create"),
            {
                "customer_name": "Farm Manager Buyer",
                "customer_phone": "0711111111",
                "customer_location": "",
                "notes": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Customer.objects.filter(customer_name="Farm Manager Buyer").exists()
        )
        self.assertEqual(
            self.client.get(reverse("accounts:user-create")).status_code,
            403,
        )

    def test_staff_is_read_only_and_cannot_see_payment_balances(self):
        self.login_as(self.staff)
        response = self.client.get(reverse("sales:order-detail", args=(self.order.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tomatoes")
        self.assertNotContains(response, "TSh 8000.00")
        self.assertNotContains(response, "Outstanding")
        self.assertNotContains(response, "Payment status")
        self.assertNotContains(response, reverse("sales:order-update", args=(self.order.pk,)))

        denied = self.client.post(
            reverse("customers:customer-create"),
            {
                "customer_name": "Unauthorized",
                "customer_phone": "0700000000",
                "customer_location": "",
                "notes": "",
            },
        )
        self.assertEqual(denied.status_code, 403)
        self.assertFalse(Customer.objects.filter(customer_name="Unauthorized").exists())

    def test_user_creation_hashes_password_and_defaults_to_inactive(self):
        self.login_as(self.administrator)
        role = Group.objects.get(name=ROLE_FARM_MANAGER)
        response = self.client.post(
            reverse("accounts:user-create"),
            {
                "first_name": "  Field  ",
                "last_name": "  Worker  ",
                "username": "new-field-worker",
                "role": role.pk,
                "password1": "Strong-Kilimanjaro-927!",
                "password2": "Strong-Kilimanjaro-927!",
            },
        )
        self.assertRedirects(response, reverse("accounts:user-list"))
        created = User.objects.get(username="new-field-worker")
        self.assertEqual(created.first_name, "Field")
        self.assertEqual(created.last_name, "Worker")
        self.assertFalse(created.is_active)
        self.assertTrue(created.check_password("Strong-Kilimanjaro-927!"))
        self.assertEqual(list(created.groups.values_list("name", flat=True)), [ROLE_FARM_MANAGER])

    def test_user_creation_validates_password_strength(self):
        self.login_as(self.administrator)
        response = self.client.post(
            reverse("accounts:user-create"),
            {
                "first_name": "",
                "last_name": "",
                "username": "weak-password-user",
                "role": Group.objects.get(name=ROLE_STAFF).pk,
                "password1": "123",
                "password2": "123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="weak-password-user").exists())

    def test_administrator_can_update_user_role_and_activation_without_password_access(self):
        target = User.objects.create_user(
            username="updatable-user",
            password=TEST_PASSWORD,
            is_active=False,
        )
        target.groups.add(Group.objects.get(name=ROLE_STAFF))
        self.login_as(self.administrator)
        edit_url = reverse("accounts:user-update", args=(target.pk,))

        self.assertContains(self.client.get(edit_url), "name=\"role\"")
        response = self.client.post(
            edit_url,
            {
                "first_name": "Updated",
                "last_name": "Account",
                "username": target.username,
                "role": Group.objects.get(name=ROLE_FARM_MANAGER).pk,
                "is_active": "on",
            },
        )
        self.assertRedirects(response, reverse("accounts:user-list"))
        target.refresh_from_db()
        self.assertEqual(target.first_name, "Updated")
        self.assertEqual(target.last_name, "Account")
        self.assertTrue(target.is_active)
        self.assertFalse(target.is_staff)
        self.assertFalse(target.is_superuser)
        self.assertTrue(target.groups.filter(name=ROLE_FARM_MANAGER).exists())
        self.assertTrue(target.check_password(TEST_PASSWORD))

    def test_normal_administrator_cannot_assign_administrator_role(self):
        self.login_as(self.administrator)
        admin_role = Group.objects.get(name=ROLE_ADMINISTRATOR)
        response = self.client.post(
            reverse("accounts:user-create"),
            {
                "first_name": "Escalation",
                "last_name": "Attempt",
                "username": "escalation-attempt",
                "role": admin_role.pk,
                "is_active": "on",
                "password1": "Strong-Kilimanjaro-927!",
                "password2": "Strong-Kilimanjaro-927!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="escalation-attempt").exists())

    def test_superuser_can_assign_administrator_group_without_superuser_status(self):
        self.login_as(self.superuser)
        response = self.client.post(
            reverse("accounts:user-create"),
            {
                "first_name": "App",
                "last_name": "Administrator",
                "username": "new-app-admin",
                "role": Group.objects.get(name=ROLE_ADMINISTRATOR).pk,
                "is_active": "on",
                "password1": "Strong-Kilimanjaro-927!",
                "password2": "Strong-Kilimanjaro-927!",
            },
        )
        self.assertRedirects(response, reverse("accounts:user-list"))
        created = User.objects.get(username="new-app-admin")
        self.assertTrue(created.is_active)
        self.assertFalse(created.is_superuser)
        self.assertFalse(created.is_staff)
        self.assertTrue(created.groups.filter(name=ROLE_ADMINISTRATOR).exists())

    def test_normal_administrator_cannot_edit_another_administrator_or_themselves(self):
        other_admin = self.create_role_user("another-admin", ROLE_ADMINISTRATOR)
        self.login_as(self.administrator)
        for target in (self.administrator, other_admin):
            with self.subTest(target=target.username):
                response = self.client.get(
                    reverse("accounts:user-update", args=(target.pk,))
                )
                self.assertEqual(response.status_code, 403)

    def test_profile_only_updates_names_and_navbar_uses_full_name_or_username(self):
        self.login_as(self.staff)
        profile_url = reverse("accounts:profile")
        response = self.client.post(
            profile_url,
            {
                "first_name": "  Asha ",
                "last_name": "  Mushi  ",
                "username": "changed-username",
                "is_active": "",
                "is_superuser": "on",
                "role": Group.objects.get(name=ROLE_ADMINISTRATOR).pk,
            },
        )
        self.assertRedirects(response, profile_url)
        self.staff.refresh_from_db()
        self.assertEqual(self.staff.first_name, "Asha")
        self.assertEqual(self.staff.last_name, "Mushi")
        self.assertEqual(self.staff.username, "farm-staff")
        self.assertTrue(self.staff.is_active)
        self.assertFalse(self.staff.is_superuser)
        self.assertTrue(self.staff.groups.filter(name=ROLE_STAFF).exists())

        response = self.client.get(reverse("dashboard:dashboard"))
        self.assertContains(response, "Asha Mushi")
        self.assertContains(response, "Staff")
        self.assertContains(response, reverse("accounts:logout"))

    def test_navbar_falls_back_to_username_and_anonymous_sees_login(self):
        self.login_as(self.staff)
        response = self.client.get(reverse("dashboard:dashboard"))
        self.assertContains(response, "farm-staff")

        self.client.logout()
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(response, reverse("accounts:login"))
        self.assertContains(response, "Log in")
        self.assertNotContains(response, "main-navigation")

    def test_user_cannot_deactivate_their_own_account(self):
        self.login_as(self.administrator)
        response = self.client.post(
            reverse(
                "accounts:user-toggle-active",
                args=(self.administrator.pk,),
            ),
            follow=True,
        )
        self.assertTrue(self.administrator.is_active)
        self.assertContains(response, "You cannot deactivate your own account.")

    def test_activation_is_a_post_only_admin_action(self):
        inactive = User.objects.create_user(
            username="inactive-worker",
            password=TEST_PASSWORD,
            is_active=False,
        )
        self.login_as(self.administrator)
        url = reverse("accounts:user-toggle-active", args=(inactive.pk,))
        self.assertEqual(self.client.get(url).status_code, 405)
        response = self.client.post(url)
        self.assertRedirects(response, reverse("accounts:user-list"))
        inactive.refresh_from_db()
        self.assertTrue(inactive.is_active)

    def test_admin_list_displays_roles_and_hides_unavailable_actions(self):
        self.login_as(self.administrator)
        response = self.client.get(reverse("accounts:user-list"))
        self.assertContains(response, "application-admin")
        self.assertContains(response, "Sales Manager")
        self.assertNotContains(
            response,
            reverse("accounts:user-update", args=(self.administrator.pk,)),
        )

    def test_admin_area_is_denied_to_non_administrator(self):
        self.login_as(self.farm_manager)
        for name in ("user-list", "user-create"):
            response = self.client.get(reverse(f"accounts:{name}"))
            self.assertEqual(response.status_code, 403)

    def test_application_administrator_does_not_get_django_admin_access(self):
        self.login_as(self.administrator)
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)

        self.login_as(self.superuser)
        self.assertEqual(self.client.get("/admin/").status_code, 200)

    def test_legacy_staff_admin_cannot_change_roles_or_view_password_hashes(self):
        legacy_staff = User.objects.create_user(
            username="legacy-staff",
            password=TEST_PASSWORD,
            is_active=True,
            is_staff=True,
        )
        legacy_staff.user_permissions.add(
            Permission.objects.get(codename="view_user"),
            Permission.objects.get(codename="change_user"),
            Permission.objects.get(codename="view_group"),
            Permission.objects.get(codename="change_group"),
        )
        self.client.force_login(legacy_staff)

        user_change = self.client.get(
            reverse("admin:auth_user_change", args=(self.staff.pk,))
        )
        self.assertEqual(user_change.status_code, 200)
        self.assertNotContains(user_change, "name=\"is_superuser\"")
        self.assertNotContains(user_change, "name=\"groups\"")
        self.assertNotContains(user_change, "name=\"password\"")

        self.client.force_login(self.superuser)
        trusted_user_change = self.client.get(
            reverse("admin:auth_user_change", args=(self.staff.pk,))
        )
        self.assertContains(trusted_user_change, "name=\"is_superuser\"")
        self.assertContains(trusted_user_change, "name=\"groups\"")
        self.assertNotContains(trusted_user_change, "name=\"password\"")

        self.client.force_login(legacy_staff)
        group_change = self.client.get(
            reverse(
                "admin:auth_group_change",
                args=(Group.objects.get(name=ROLE_ADMINISTRATOR).pk,),
            )
        )
        self.assertEqual(group_change.status_code, 403)
