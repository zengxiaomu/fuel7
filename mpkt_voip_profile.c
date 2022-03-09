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

int mpkt_rnd_seq[100];
int voip_rate_talking = 370;  /* 12200 / 33 packets per second */
int voip_rate_silent = 37;  /* UNSPECIFIED. set it to 37 for now */
int voip_pkt_size = 33;

void seed_rnd()
{
  srand(time(NULL));
}

bool do_send_pkt_talking()
{
  int i = rand() % 1000;
  return (i < voip_rate_talking);
}

bool do_send_pkt_silent()
{
  int i = rand() % 1000;
  return (i < voip_rate_silent);
}

void mpkt_read_rnd(char *fn)
{
  FILE *fp;
  char line[80];
  int i, n;

  i = 0;
  fp = fopen(fn, "r");
  while (fgets(line, 80, fp)) {
    line[strcspn(line, "\n")] = 0;  /* remove the \n character */
    if (line[0] == '#') {
      printf("%s\n", line);
      continue; /* skip comments */
    }
    sscanf(line, "%d", &n);
    mpkt_rnd_seq[i] = n;
    /* printf("%d\n", n); */
    i++;
    if (i >= 100) {
      break;
    }
  }
}

void mpkt_read_rnd_exponential_seq()
{
  mpkt_read_rnd("rnd_exponential.txt");
}

/*
  voip active state functions
 */

int voip_get_delta() {  /* MASSIVE amount of working getting done in here */
  /* all those static variables should be in an object eventually */
  static int abs_time = 0;
  static int last_sent = 0;
  static int state_now = 1;  /* 1: talking  0: silent */
  static int next_state_change = 0;
  static int rnd_seq_index = 0; 
  bool do_send_pkt;
  int delta;

  if (abs_time == 0) {  /* initialization code goes here */
    seed_rnd();
    mpkt_read_rnd_exponential_seq();
  }

  abs_time++;
  if (state_now == 1) {
    do_send_pkt = do_send_pkt_talking();
  } else {
    do_send_pkt = do_send_pkt_silent();
  }

  if (do_send_pkt) {
    delta = abs_time - last_sent;
    last_sent = abs_time;
  } else {
    delta = 0;  /* 0 means dont send packet */
  }

  if (abs_time >= next_state_change) {  /* it should never be greater but just in case */
    if (next_state_change > 0) {  /* for first time, don't change state */
      /*  toggle state */
      if (state_now == 1) {
        state_now = 0;
        voip_pkt_size = 7;
      } else {
        state_now = 1;
        voip_pkt_size = 33;
      }
    }
    next_state_change = abs_time + mpkt_rnd_seq[rnd_seq_index];
    rnd_seq_index++;
  }

  return delta;
}

mpkt_profile_t *mpkt_voip_active_profile_create(const mpkt_profile_ops_t *ops, const mpkt_protocol_attr_t *proto_attr, mp_hkv_node_t *cfg)
{
  mpkt_voip_profile_t *profile;

  profile = malloc(sizeof(*profile));
  mpkt_profile_init(&profile->profile, ops);

  return &profile->profile;
  /*
    proto_attr and cfg are unused, need to find out how to use them
   */
}

void mpkt_voip_active_profile_destroy(mpkt_profile_t *profile)
{
  mpkt_voip_profile_t *voip_profile = MP_CONTAINER_OF(profile, mpkt_voip_profile_t, profile);
  free(voip_profile);
}

void mpkt_voip_active_profile_fill(mpkt_profile_t *profile, mpkt_packet_attr_t *attr) 
{
  int delta;

  delta = voip_get_delta();

  if (delta > 0) {
    mpkt_packet_attr_init(
      attr,
      false, /* start_of_burst is always false for voip */
      voip_pkt_size, /* packet size */
      US_TO_NS(MS_TO_US(delta)));
  }
}

/*
  voip silent state functions
 */

mpkt_profile_t *mpkt_voip_silent_profile_create(const mpkt_profile_ops_t *ops, const mpkt_protocol_attr_t *proto_attr, mp_hkv_node_t *cfg)
{
  mpkt_voip_profile_t *profile;

  profile = malloc(sizeof(*profile));
  mpkt_profile_init(&profile->profile, ops);

  return &profile->profile;
}

void mpkt_voip_silent_profile_destroy()
{
}

void mpkt_voip_silent_profile_fill() 
{
}


