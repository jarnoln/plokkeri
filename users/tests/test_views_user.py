from django.core.urlresolvers import reverse
from django.contrib import auth
from .ext_test_case import ExtTestCase


class UserListTest(ExtTestCase):
    def test_reverse(self):
        self.assertEqual(reverse('user_list'), '/users/')

    def test_uses_correct_template(self):
        self.create_and_log_in_user()
        response = self.client.get(reverse('user_list'))
        self.assertTemplateUsed(response, 'auth/user_list.html')

    def test_default_context(self):
        user = self.create_and_log_in_user()
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.context['user_list'].count(), 1)
        self.assertEqual(response.context['user_list'][0], user)
        user_2 = auth.get_user_model().objects.create(username='user_2')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.context['user_list'].count(), 2)
        self.assertContains(response, user_2.username)
        user_3 = auth.get_user_model().objects.create(username='user_3')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.context['user_list'].count(), 3)
        self.assertContains(response, user_3.username)


class UserDetailTest(ExtTestCase):
    def test_reverse(self):
        self.assertEqual(reverse('profile'), '/accounts/profile/')
        self.assertEqual(reverse('user_detail', args=['shinji']), '/user/shinji/')

    def test_uses_correct_template(self):
        user = auth.get_user_model().objects.create(username='shinji')
        response = self.client.get(reverse('user_detail', args=[user.username]))
        self.assertTemplateUsed(response, 'auth/profile.html')
        self.create_and_log_in_user()
        response = self.client.get(reverse('profile'))
        self.assertTemplateUsed(response, 'auth/profile.html')

    def test_default_content(self):
        user = self.create_and_log_in_user()
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated())
        self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['object'], user)
        self.assertContains(response, 'Profile')
        html = response.content.decode('utf8')
        # print(html)
        self.assertTrue(html.startswith('<!DOCTYPE html>'))
        self.assertInHTML(user.username, html)
        self.assertInHTML(user.email, html)
        self.assertInHTML('Delete account', html)

    def test_viewing_other_user(self):
        target_user = auth.get_user_model().objects.create(username='shinji', email='shinji@nerv.org')
        user = self.create_and_log_in_user()
        response = self.client.get(reverse('user_detail', args=[target_user.username]))
        # self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['object'], target_user)
        self.assertContains(response, 'Profile')
        html = response.content.decode('utf8')
        self.assertTrue(html.startswith('<!DOCTYPE html>'))
        self.assertInHTML(target_user.username, html)
        self.assertInHTML(target_user.email, html)
        self.assertNotIn('Delete account', html)

    def test_cant_view_profile_if_not_logged_in(self):
        auth.get_user_model().objects.create(username='user')
        response = self.client.get(reverse('profile'), follow=True)
        self.assertTemplateUsed(response, 'account/login.html')


class UpdateUserTest(ExtTestCase):
    def test_reverse_task_edit(self):
        self.assertEqual(reverse('user_update', args=['test_user']),
                         '/user/test_user/edit/')

    def test_uses_correct_template(self):
        user = self.create_and_log_in_user()
        response = self.client.get(reverse('user_update', args=[user.username]))
        self.assertTemplateUsed(response, 'auth/user_form.html')

    def test_default_context(self):
        user = self.create_and_log_in_user()
        response = self.client.get(reverse('user_update', args=[user.username]))
        self.assertEqual(response.context['user'], user)
        self.assertEqual(response.context['message'], '')

    def test_can_update_user(self):
        user = self.create_and_log_in_user()
        response = self.client.post(reverse('user_update', args=[user.username]), {
            'first_name': 'Bruce',
            'last_name': 'Wayne'
        }, follow=True)
        self.assertEqual(auth.get_user_model().objects.all().count(), 1)
        user = auth.get_user_model().objects.all()[0]
        self.assertEqual(user.first_name, 'Bruce')
        self.assertEqual(user.last_name, 'Wayne')
        self.assertTemplateUsed(response, 'auth/profile.html')

    def test_cant_update_user_if_not_logged_in(self):
        user = auth.get_user_model().objects.create(username='user', email='user@default.com',
                                                    first_name='Clark', last_name='Kent')
        response = self.client.post(reverse('user_update', args=[user.username]), {
            'first_name': 'Bruce',
            'last_name': 'Wayne'
        }, follow=True)
        self.assertEqual(auth.get_user_model().objects.all().count(), 1)
        user = auth.get_user_model().objects.all()[0]
        self.assertEqual(user.first_name, 'Clark')
        self.assertEqual(user.last_name, 'Kent')
        self.assertTemplateUsed(response, 'account/login.html')

    def test_cant_update_other_users(self):
        logged_user = self.create_and_log_in_user()
        other_user = auth.get_user_model().objects.create(username='other', email='other@default.com',
                                                          first_name='Clark', last_name='Kent')
        self.assertEqual(auth.get_user_model().objects.all().count(), 2)
        response = self.client.post(reverse('user_update', args=[other_user.username]),
                                    {'username': 'other', 'first_name': 'Bruce'},
                                    follow=True)
        self.assertEqual(auth.get_user_model().objects.all().count(), 2)
        user = auth.get_user_model().objects.get(username='other')
        self.assertEqual(user.first_name, 'Clark')
        self.assertTemplateUsed(response, '404.html')


class DeleteUserPageTest(ExtTestCase):
    def test_reverse_blog_delete(self):
        self.assertEqual(reverse('user_delete', args=['test_user']), '/user/test_user/delete/')

    def test_uses_correct_template(self):
        user = self.create_and_log_in_user()
        response = self.client.get(reverse('user_delete', args=[user.username]))
        self.assertTemplateUsed(response, 'auth/user_confirm_delete.html')

    def test_can_delete_user(self):
        user = self.create_and_log_in_user()
        self.assertEqual(auth.models.User.objects.count(), 1)
        self.client.post(reverse('user_delete', args=[user.username]), {}, follow=True)
        self.assertEqual(auth.models.User.objects.count(), 0)

    def test_404_no_user(self):
        self.create_and_log_in_user()
        response = self.client.get(reverse('user_delete', args=['dummy_user']))
        # print(response.content.decode('utf8'))
        self.assertTemplateUsed(response, '404.html')

    def test_cant_delete_user_if_not_logged_in(self):
        user = auth.models.User.objects.create(username='user')
        self.assertEqual(auth.models.User.objects.all().count(), 1)
        response = self.client.post(reverse('user_delete', args=[user.username]), {}, follow=True)
        # print(response.content.decode('utf8'))
        self.assertEqual(auth.models.User.objects.all().count(), 1)
        self.assertTemplateUsed(response, 'account/login.html')

    def test_cant_delete_other_users(self):
        self.create_and_log_in_user()
        other_user = auth.models.User.objects.create(username='other_user')
        self.assertEqual(auth.models.User.objects.all().count(), 2)
        response = self.client.post(reverse('user_delete', args=[other_user.username]), {}, follow=True)
        self.assertEqual(auth.models.User.objects.all().count(), 2)
        self.assertTemplateUsed(response, '404.html')
