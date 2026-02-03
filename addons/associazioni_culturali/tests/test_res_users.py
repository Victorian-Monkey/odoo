# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestResUsers(TransactionCase):

    def setUp(self):
        super(TestResUsers, self).setUp()
        self.User = self.env['res.users']
        self.Associato = self.env['associato']
        self.user = self.User.create({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'test@example.com',
        })

    def test_associato_ids_relation(self):
        """L'utente ha la relazione inversa associato_ids verso i profili reclamati"""
        associato = self.Associato.create({
            'email': 'test@example.com',
            'user_id': self.user.id,
        })
        self.assertIn(associato, self.user.associato_ids)
        self.assertEqual(len(self.user.associato_ids), 1)
