#include "mpkt_stream_factory.h"

typedef struct
{
  mpkt_profile_t profile;
} mpkt_voip_profile_t;

mpkt_profile_t* mpkt_voip_profile_create(const mpkt_profile_ops_t *ops, const mpkt_protocol_attr_t *proto_attr, mp_hkv_node_t *cfg)
{
  mpkt_voip_profile_t *profile;

  profile = malloc(sizeof(*profile));

  mpkt_profile_init(&profile->profile, ops);

  return &profile->profile;
}

void mpkt_voip_profile_destroy(mpkt_profile_t *profile)
{
  mpkt_voip_profile_t *voip_profile = MP_CONTAINER_OF(profile, mpkt_voip_profile_t, profile);
  free(voip_profile);
}

void mpkt_voip_profile_fill(mpkt_profile_t *profile, mpkt_packet_attr_t *attr)
{
  mpkt_packet_attr_init(
    attr,
    false, // start_of_burst is always false for voip
    1470,
    US_TO_NS(1000));
}

static const mpkt_profile_ops_t g_mpkt_voip_profile_ops =
{
  .create = mpkt_voip_profile_create,
  .destroy = mpkt_voip_profile_destroy,
  .fill = mpkt_voip_profile_fill
};

MPKT_PROFILE(voip, 0, g_mpkt_voip_profile_ops);

/*
 random exponential sequence
*/

void mpkt_read_rnd(char *fn)
{
  FILE *fp;
  char line[80];

  fp = fopen(fn, "r");
  while (fgets(line, 80, fp)) {
    printf("%s\n", line);
  }
}

void mpkt_read_rnd_exponential_seq()
{
  mpkt_read_rnd("rnd_exponential.txt");
}


