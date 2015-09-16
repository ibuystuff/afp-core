#!/usr/bin/env python
# -*- coding: utf-8 -*-

from socket import gethostbyaddr

from aws_federation_proxy.provider import BaseProvider


class ProviderByIP(BaseProvider):
    """Uses IP address/FQDN as username, returning exactly one role

    The account name must be configured, only the role name is determined by
    the IP/FQDN.
    """

    def get_accounts_and_roles(self):
        """Return a dict with one account and one aws role"""
        self.client_fqdn = gethostbyaddr(self.user)[0]
        self._get_role_name()
        reason = "Machine {0} (FQDN {1}) matched the role {2}".format(
            self.user, self.client_fqdn, self.role_name)
        return {self.config["account_name"]: set([(self.role_name, reason)])}

    def _get_role_name(self):
        """Translate self.user / self.client_fqdn into self.role_name"""
        raise NotImplementedError  # pragma: no cover


class Provider(ProviderByIP):
    """Apply Immobilienscout24 host name pattern, returning exactly one role"""

    def _get_role_name(self):
        """Determined the aws role name to a given ip address"""
        allowed_domains = self.config['allowed_domains']

        self.client_host, self.client_domain = self.client_fqdn.split(".", 1)
        if self.client_domain not in allowed_domains:
            raise Exception("Client IP {0} (FQDN {1}) is not permitted".format(
                            self.user, self.client_fqdn))

        if len(self.client_host) != 8:
            raise Exception("Client {0} has an invalid name".format(self.client_fqdn))

        loctyp = self._normalize_loctyp()
        self.role_name = loctyp

    def _normalize_loctyp(self):
        """Return the normalized (ber/ham -> pro) loctyp of self.client_host"""
        if self.client_host.startswith(("ber", "ham")):
            return "pro" + self.client_host[3:6]
        else:
            return self.client_host[:6]
