from __future__ import print_function, absolute_import, unicode_literals, division

from aws_federation_proxy.provider import ProviderByGroups

import grp
from six import text_type


class Provider(ProviderByGroups):
    """Uses the builtin grp module to retrieve group information"""

    def get_group_list(self):
        return [g.gr_name for g in grp.getgrall() if self.user.lower() in map(text_type.lower, g.gr_mem)]
